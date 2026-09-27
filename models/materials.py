import math


class Material:
    """Строительный материал."""

    def __init__(
        self,
        material_id: int,
        name: str,
        unit: str,
        price: float,
        coverage: float,
    ) -> None:
        """Создать объект материала."""
        self.id = material_id
        self.name = name
        self.unit = unit
        self.price = price
        self.coverage = coverage

    def calculate_quantity(self, area: float) -> int:
        """Рассчитать количество материала для заданной площади."""
        return math.ceil(area / self.coverage)

    def calculate_cost(self, quantity: int) -> float:
        """Рассчитать стоимость материала."""
        return round(quantity * self.price, 2)

    @classmethod
    def from_data(cls, data: dict) -> "Material":
        """Создать материал из словаря."""
        return cls(
            material_id=data["id"],
            name=data["name"],
            unit=data["unit"],
            price=data["price"],
            coverage=data["coverage"],
        )

    def to_data(self) -> dict:
        """Преобразовать материал в словарь."""
        return {
            "id": self.id,
            "name": self.name,
            "unit": self.unit,
            "price": self.price,
            "coverage": self.coverage,
        }

    def __str__(self) -> str:
        """Строковое представление материала."""
        return f"[{self.id}] {self.name} — {self.price} руб./{self.unit}"
