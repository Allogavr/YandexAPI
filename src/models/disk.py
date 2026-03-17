from pydantic import BaseModel, Field
from typing import Optional, List


class User(BaseModel):
    login: str = Field(..., description="Логин пользователя")
    display_name: str = Field(..., description="Отображаемое имя")


class DiskResponse(BaseModel):
    user: User


class ApiError(BaseModel):
    error: str = Field(..., description="Код ошибки")
    message: Optional[str] = Field(None, description="Сообщение об ошибке")
    description: Optional[str] = Field(None, description="Описание ошибки")


class LinkResponse(BaseModel):
    href: str = Field(..., description="URL для получения информации")
    method: str = Field(..., description="HTTP метод")
    templated: bool = Field(..., description="Является ли URL шаблоном")


class OperationResponse(BaseModel):
    href: str = Field(..., description="URL для проверки статуса")
    method: str = Field(..., description="HTTP метод")
    templated: bool = Field(..., description="Является ли URL шаблоном")


class TrashResource(BaseModel):
    path: str = Field(..., description="Путь в корзине (с префиксом trash:/)")
    name: str = Field(..., description="Имя")
    type: str = Field(..., description="Тип: 'file' или 'dir'")
    created: Optional[str] = None
    modified: Optional[str] = None
    size: Optional[int] = None


class TrashContents(BaseModel):
    items: List[TrashResource] = Field(..., description="Список ресурсов")
    limit: int = Field(..., description="Лимит выдачи")
    offset: int = Field(..., description="Смещение")


class ResourceInfo(BaseModel):
    path: str = Field(..., description="Путь")
    name: str = Field(..., description="Имя")
    type: str = Field(..., description="Тип")
    created: Optional[str] = None
    modified: Optional[str] = None
    size: Optional[int] = None
