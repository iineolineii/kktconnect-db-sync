from uuid import uuid4

from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str = Field(unique=True)
    email: str | None = Field(default=None, unique=True)
    confirmed: bool = False

    token: str = Field(default_factory=lambda: uuid4().hex, unique=True, index=True)


class Employee(SQLModel, table=True):
    # Personal info
    name:      str = Field(primary_key=True)
    snils:     str = Field(unique=True)
    email:     str | None = Field(default=None, unique=True)

    # Status
    confirmed: bool = False
    invited:   bool = False
    assigned:  bool = False

    # Role
    is_teacher:  bool = False
    is_admin:    bool = False
    is_director: bool = False

    token: str = Field(
        default_factory=lambda: uuid4().hex,
        unique=True
    )


__all__ = ["User", "Employee"]
