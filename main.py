import math

FUNKCJE = {
    # 1. Funkcja liniowa (Linear)
    1: {"nazwa": "2x - 1",
        "f": lambda x: 2 * x - 1,
        "xrange": (-5, 5),
        "yrange": (-11, 9)}, # Zakres y obliczony dla x z xrange

    # 2. Funkcja |x| (Absolute value)
    2: {"nazwa": "|x|",
        "f": lambda x: abs(x),
        "xrange": (-5, 5),
        "yrange": (-1, 6)}, # Zakres y obejmuje min=0 i dodaje margines

    # 3. Funkcja wielomianowa (Polynomial)
    3: {"nazwa": "x^4 - 3x^2 + x - 2",
        "f": lambda x: x**4 - 3*x**2 + x - 2,
        "xrange": (-3, 3),
        "yrange": (-10, 60), # Przybliżony zakres y dla x z xrange
        "wspolczynniki": (1, 0, -3, 1, -2)}, # Współczynniki od najwyższej potęgi

    # 4. Funkcja trygonometryczna (Trigonometric)
    4: {"nazwa": "cos(2x) + sin(x)",
        "f": lambda x: math.cos(2 * x) + math.sin(x),
        "xrange": (-2 * math.pi, 2 * math.pi), # Typowy zakres dla funkcji trygonometrycznych
        "yrange": (-2.5, 2.5)}, # Przybliżony zakres wartości

    # 5. Złożenie funkcji (Composition)
    5: {"nazwa": "e^|x-1| - 2",
        "f": lambda x: math.exp(abs(x - 1)) - 2,
        "xrange": (-3, 5),
        "yrange": (-2, 55)}, # Zakres y obliczony dla x z xrange (e^4 - 2 ~ 52.6)
}

def funkcja_menu():
    print("Wybierz funkcję:")
    for i in FUNKCJE:
        print(f"{i}. {FUNKCJE[i]['nazwa']}")
    print ("5. Zakończ program")
    while True:
        try:
            wybor = int(input("Wybierz numer funkcji: "))
            if wybor in FUNKCJE:
                return FUNKCJE[wybor], wybor, True
            elif wybor == 5:
                return None, None, False
            raise ValueError
        except ValueError:
            print("Błędny wybór, spróbuj ponownie!")


def przedzial():
    print("Podaj przedział:")
    while True:
        try:
            a = float(input("a: "))
            b = float(input("b: "))
            if a >= b:
                raise ValueError
            return a, b
        except ValueError:
            print("Błędny przedział, spróbuj ponownie!")
