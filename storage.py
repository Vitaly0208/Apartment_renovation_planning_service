import json


def load_data(filename: str) -> list[dict]:
    """Загрузить данные из JSON-файла."""
    try:
        with open(filename, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError as error:
        print(f"Ошибка чтения JSON: {error}")
        return []


def save_data(filename: str, data: list[dict]) -> None:
    """Сохранить данные в JSON-файл."""
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
