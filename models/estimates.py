from .rooms import Room
from .users import User


class Estimate:
    """Смета ремонта помещения для конкретного пользователя."""

    def __init__(
        self,
        estimate_id: int,
        room: Room,
        user: User,
        materials_cost: float,
        works_cost: float,
    ) -> None:
        """Создать объект сметы."""
        self.id = estimate_id
        self.room = room
        self.user = user
        self.materials_cost = materials_cost
        self.works_cost = works_cost
        self.total = round(materials_cost + works_cost, 2)

    def check_budget(self, budget: float) -> dict:
        """Проверить достаточность бюджета."""
        if budget >= self.total:
            return {
                "is_sufficient": True,
                "message": (
                    f"Бюджет достаточен. "
                    f"Остаток: {round(budget - self.total, 2)} руб."
                ),
            }
        return {
            "is_sufficient": False,
            "message": (
                f"Недостаточно средств. "
                f"Не хватает: {round(self.total - budget, 2)} руб."
            ),
        }

    @classmethod
    def from_data(cls, data: dict, room: Room, user: User) -> "Estimate":
        """Создать смету из словаря."""
        return cls(
            estimate_id=data["id"],
            room=room,
            user=user,
            materials_cost=data["materials_cost"],
            works_cost=data["works_cost"],
        )

    def to_data(self) -> dict:
        """Преобразовать смету в словарь."""
        return {
            "id": self.id,
            "room_id": self.room.id,
            "user_id": self.user.id,
            "materials_cost": self.materials_cost,
            "works_cost": self.works_cost,
            "total": self.total,
        }

    def __str__(self) -> str:
        """Строковое представление сметы."""
        return (
            f"[{self.id}] {self.user.name} → {self.room.name}: "
            f"материалы {self.materials_cost} + "
            f"работы {self.works_cost} = {self.total} руб."
        )
