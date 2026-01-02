from typing import Optional

from pydantic import BaseModel, field_validator
from shared.utils.enums import RolesEnum


class UsersBase(BaseModel):
    email: str
    role: Optional[str] = "user"

    @field_validator('email')
    @classmethod
    def email_validator(cls, v):
        email_regex = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        if not re.match(email_regex, v):
            raise ValueError("Email incorrect format (ex: nume@domeniu.com)")
        return v

    @field_validator('role')
    @classmethod
    def role_validator(cls, v):
        if v not in RolesEnum:
            raise ValueError(f"Role must be one of {RolesEnum}")
        return v


class UsersUpdate(BaseModel):
    email: Optional[str] = None
    role: Optional[str] = None
    password_hash: Optional[str] = None
