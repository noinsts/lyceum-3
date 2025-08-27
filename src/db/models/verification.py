from sqlalchemy import BigInteger, Boolean, UniqueConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseModel


class TeacherVerificationModel(BaseModel):
    __tablename__ = 'teacher_verification'
    __table_args__ = (
        UniqueConstraint("teacher_id", name="uq_teacher_id"),
    )

    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    teacher_id: Mapped[int] = mapped_column(ForeignKey("teachers.id"), nullable=False, unique=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    teacher = relationship("TeacherModel", back_populates="verification")
