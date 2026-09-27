from .rooms import Room


class Estimate:
    """Смета ремонта помещения."""

    def __init__(
        self,
        estimate_id: int,
        room: Room,
        materials_cost: float,
        works_cost: float,
    ) -> None:
        """Создать объект сметы."""
        self.id = estimate_id
        self.room = room
        self.materials_cost = materials_cost
        self.works_cost = works_cost
        self.total = round(materials_cost + works_cost, 2)

    def check_budget(self, budget: float) -> dict:
        """Проверить достаточность бюджета."""
        if budget >= self.total:
            return {
                "is_sufficient": True,
                "message": f"Бюджет достаточен. Остаток: "
                           f"{round(budget - self.total, 2)} руб.",
            }
        return {
            "is_sufficient": False,
            "message": f"Недостаточно средств. Не хватает: "
                       f"{round(self.total - budget, 2)} руб.",
        }

    @classmethod
    def from_data(cls, data: dict, room: Room) -> "Estimate":
        """Создать смету из словаря."""
        estimate = cls(
            estimate_id=data["id"],
            room=room,
            materials_cost=data["materials_cost"],
            works_cost=data["works_cost"],
        )
        return estimate

    def to_data(self) -> dict:
        """Преобразовать смету в словарь."""
        return {
            "id": self.id,
            "room_id": self.room.id,
            "materials_cost": self.materials_cost,
            "works_cost": self.works_cost,
            "total": self.total,
        }

    def __str__(self) -> str:
        """Строковое представление сметы."""
        return (
            f"[{self.id}] {self.room.name}: "
            f"материалы {self.materials_cost} + "
            f"работы {self.works_cost} = {self.total} руб."
        )
