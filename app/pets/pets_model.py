"""Modelo SQLAlchemy de Pet (tabla `pets`). Mismo estilo que StudentModel."""

import uuid

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, UniqueConstraint

from app.shared.database import Base
from app.shared.datetimes import utc_now


class PetModel(Base):
    __tablename__ = "pets"
    __table_args__ = (
        # Regla del README: el nombre es único dentro de un mismo estudiante.
        UniqueConstraint("studentId", "name", name="uq_pets_studentId_name"),
    )

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # ondelete="CASCADE" es IMPORTANTE: StudentModel no tiene relationship con
    # pets, así que al borrar un estudiante son las mascotas las que se borran
    # por cascada a nivel de base de datos (DELETE /api/students/:id).
    studentId = Column(
        String(36),
        ForeignKey("students.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    name = Column(String(50), nullable=False)
    species = Column(String(50), nullable=False)
    age = Column(Integer, nullable=True)

    createdAt = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updatedAt = Column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False
    )
