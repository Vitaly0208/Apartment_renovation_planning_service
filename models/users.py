class User:
    """Пользователь системы (заказчик ремонта)."""

    def __init__(
        self,
        user_id: int,
        name: str,
        phone: str,
        email: str,
    ) -> None:
        """Создать объект пользователя."""
        self.id = user_id
        self.name = name
        self.phone = phone
        self.email = email

    @classmethod
    def from_data(cls, data: dict) -> "User":
        """Создать пользователя из словаря."""
        return cls(
            user_id=data["id"],
            name=data["name"],
            phone=data["phone"],
            email=data["email"],
        )

    def to_data(self) -> dict:
        """Преобразовать пользователя в словарь."""
        return {
            "id": self.id,
            "name": self.name,
            "phone": self.phone,
            "email": self.email,
        }

    def __str__(self) -> str:
        """Строковое представление пользователя."""
        return f"[{self.id}] {self.name} ({self.phone})"
