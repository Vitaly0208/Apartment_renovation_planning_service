from typing import List
from .rooms import Room
from .users import User
from .materials import Material

class Estimate:
    def __init__(
        self,
        estimate_id: int,
        room: Room,
        user: User,
        materials: List[Material],
        works_cost: float,
    ) -> None:
        self.id = estimate_id
        self.room = room
        self.user = user
        self.materials = materials
        self.works_cost = works_cost
        self.materials_cost = round(sum(m.price for m in materials), 2)
        self.total = round(self.materials_cost + self.works_cost, 2)

    def check_budget(self, budget: float) -> dict:
        if budget >= self.total:
            return {
                "is_sufficient": True,
                "message": f"Бюджет достаточен. Остаток: {round(budget - self.total, 2)} руб.",
            }
        return {
            "is_sufficient": False,
            "message": f"Недостаточно средств. Не хватает: {round(self.total - budget, 2)} руб.",
        }

    @classmethod
    def from_data(cls, data: dict, room: Room, user: User, all_materials: List[Material]) -> "Estimate":
        """Создать смету из словаря, восстанавливая объекты материалов по их ID."""
        materials_in_estimate = [
            m for m in all_materials if m.id in data["material_ids"]
        ]
        return cls(
            estimate_id=data["id"],
            room=room,
            user=user,
            materials=materials_in_estimate,
            works_cost=data["works_cost"],
        )

    def to_data(self) -> dict:
        """Преобразовать смету в словарь для сохранения в JSON."""
        return {
            "id": self.id,
            "room_id": self.room.id,
            "user_id": self.user.id,
            "material_ids": [m.id for m in self.materials], # Сохраняем только ID
            "works_cost": self.works_cost,
            "total": self.total,
        }

    def __str__(self) -> str:
        materials_names = ", ".join([m.name for m in self.materials])
        return (
            f"[{self.id}] {self.user.name} → {self.room.name}: "
            f"материалы ({materials_names}) = {self.materials_cost} руб. + "
            f"работы = {self.works_cost} руб. | Итого: {self.total} руб."
        )