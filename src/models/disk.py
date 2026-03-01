from pydantic import BaseModel, Field
from typing import Optional


class User(BaseModel):
    login: str = Field(..., description="Логин пользователя")
    display_name: str = Field(..., description="Отображаемое имя")


class DiskResponse(BaseModel):
    user: User


class ApiError(BaseModel):
    error: str = Field(..., description="Код ошибки")
    message: Optional[str] = Field(None, description="Сообщение об ошибке")
    description: Optional[str] = Field(None, description="Описание ошибки")
