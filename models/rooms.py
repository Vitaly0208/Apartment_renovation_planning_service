class Room:
    """Помещение для ремонта."""

    def __init__(
        self,
        room_id: int,
        name: str,
        length: float,
        width: float,
        height: float,
    ) -> None:
        """Создать объект помещения."""
        self.id = room_id
        self.name = name
        self.length = length
        self.width = width
        self.height = height

    def calculate_floor_area(self) -> float:
        """Рассчитать площадь пола."""
        return round(self.length * self.width, 2)

    def calculate_wall_area(self) -> float:
        """Рассчитать площадь стен."""
        perimeter = 2 * (self.length + self.width)
        return round(perimeter * self.height, 2)

    def is_suitable_for(self, min_area: float) -> bool:
        """Проверить, подходит ли помещение по площади."""
        return self.calculate_floor_area() >= min_area

    @classmethod
    def from_data(cls, data: dict) -> "Room":
        """Создать помещение из словаря."""
        return cls(
            room_id=data["id"],
            name=data["name"],
            length=data["length"],
            width=data["width"],
            height=data["height"],
        )

    def to_data(self) -> dict:
        """Преобразовать помещение в словарь."""
        return {
            "id": self.id,
            "name": self.name,
            "length": self.length,
            "width": self.width,
            "height": self.height,
        }

    def __str__(self) -> str:
        """Строковое представление помещения."""
        area = self.calculate_floor_area()
        return f"[{self.id}] {self.name} — {area} кв.м"
