"""Repositorio de Pet. Mismo estilo que StudentsRepository:

- Cada método recibe `db` como primer parámetro.
- Solo consulta y modifica (flush). NUNCA hace commit: eso lo decide el
  servicio con `transaction(db)`.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.pets.pets_model import PetModel


class PetsRepository:
    def find_all_by_student(self, db: Session, student_id: str) -> list[PetModel]:
        stmt = (
            select(PetModel)
            .where(PetModel.studentId == student_id)
            .order_by(PetModel.createdAt.desc())
        )
        return list(db.scalars(stmt))

    def find_by_id(
        self, db: Session, student_id: str, pet_id: str
    ) -> PetModel | None:
        stmt = select(PetModel).where(
            PetModel.id == pet_id, PetModel.studentId == student_id
        )
        return db.scalars(stmt).first()

    # Esta firma la usa StudentsService.create (no cambiarla).
    def find_by_student_and_name(
        self, db: Session, student_id: str, name: str
    ) -> PetModel | None:
        stmt = select(PetModel).where(
            PetModel.studentId == student_id, PetModel.name == name
        )
        return db.scalars(stmt).first()

    # Esta firma también la usa StudentsService.create. El flush es necesario:
    # así la siguiente consulta del mismo request ve la mascota recién agregada
    # (detecta nombres repetidos dentro de `pets[]`).
    def add(self, db: Session, pet: PetModel) -> PetModel:
        db.add(pet)
        db.flush()
        return pet

    def delete(self, db: Session, pet: PetModel) -> None:
        db.delete(pet)
        db.flush()


pets_repository = PetsRepository()
