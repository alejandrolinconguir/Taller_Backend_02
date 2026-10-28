"""Servicio de Pet. Mismo estilo que StudentsService.

Las escrituras van dentro de `with transaction(db):` (commit si todo sale bien,
rollback si algo falla). Los repositorios solo hacen flush.
"""

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.pets.pets_model import PetModel
from app.pets.pets_repository import PetsRepository, pets_repository
from app.pets.pets_schemas import CreatePetDto, Pet, PetList, UpdatePetDto
from app.shared.datetimes import utc_now
from app.shared.exceptions import conflict
from app.shared.transactions import transaction
from app.students.students_repository import StudentsRepository, students_repository

# Mismo mensaje que usa StudentsService.create para mascotas repetidas.
NAME_TAKEN = {"name": {"message": "Ya tienes una mascota con ese nombre"}}


class PetsService:
    def __init__(self, repository: PetsRepository, students: StudentsRepository) -> None:
        self.repository = repository
        self.students_repository = students

    def find_all(self, db: Session, student_id: str) -> PetList:
        self._assert_student_exists(db, student_id)
        pets = [
            Pet.model_validate(p)
            for p in self.repository.find_all_by_student(db, student_id)
        ]

        return PetList(total=len(pets), items=pets)

    def create(self, db: Session, student_id: str, data: CreatePetDto) -> Pet:
        self._assert_student_exists(db, student_id)
        self._assert_name_available(db, student_id, data.name)

        now = utc_now()

        try:
            with transaction(db):
                pet = self.repository.add(
                    db,
                    PetModel(
                        studentId=student_id,
                        name=data.name,
                        species=data.species,
                        age=data.age,
                        createdAt=now,
                        updatedAt=now,
                    ),
                )
                return Pet.model_validate(pet)
        except IntegrityError:
            raise conflict(NAME_TAKEN) from None

    def update(
        self, db: Session, student_id: str, pet_id: str, data: UpdatePetDto
    ) -> Pet:
        existing = self._find_model(db, student_id, pet_id)

        if data.name is not None:
            self._assert_name_available(db, student_id, data.name, except_id=pet_id)

        try:
            with transaction(db):
                for field, value in data.model_dump(exclude_none=True).items():
                    setattr(existing, field, value)
                existing.updatedAt = utc_now()
                db.flush()
                return Pet.model_validate(existing)
        except IntegrityError:
            raise conflict(NAME_TAKEN) from None

    def delete(self, db: Session, student_id: str, pet_id: str) -> Pet:
        existing = self._find_model(db, student_id, pet_id)

        with transaction(db):
            deleted = Pet.model_validate(existing)
            self.repository.delete(db, existing)

        return deleted

    # --- auxiliares ---------------------------------------------------------
    def _assert_student_exists(self, db: Session, student_id: str) -> None:
        if self.students_repository.find_by_id(db, student_id) is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Estudiante no encontrado",
            )

    def _assert_name_available(
        self,
        db: Session,
        student_id: str,
        name: str,
        except_id: str | None = None,
    ) -> None:
        existing = self.repository.find_by_student_and_name(db, student_id, name)

        if existing is not None and existing.id != except_id:
            raise conflict(NAME_TAKEN)

    def _find_model(self, db: Session, student_id: str, pet_id: str) -> PetModel:
        self._assert_student_exists(db, student_id)
        pet = self.repository.find_by_id(db, student_id, pet_id)

        if pet is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Mascota no encontrada",
            )

        return pet


pets_service = PetsService(pets_repository, students_repository)
