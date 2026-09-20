def input_int(prompt: str) -> int:
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("Ошибка: введите целое число.")


def input_float(prompt: str) -> float:
    while True:
        try:
            return float(input(prompt))
        except ValueError:
            print("Ошибка: введите число.")


def input_positive_float(prompt: str) -> float:
    while True:
        value = input_float(prompt)
        if value > 0:
            return value
        print("Ошибка: число должно быть положительным.")
