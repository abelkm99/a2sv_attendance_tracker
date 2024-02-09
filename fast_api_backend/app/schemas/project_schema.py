from pydantic import BaseModel


"""
class Project(Base):
    __tablename__ = "project"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    archived: Mapped[bool] = mapped_column(
        Boolean, server_default=false(), nullable=False
    )

"""


class ProjectBase(BaseModel):
    id: int
    name: str
    archived: bool
