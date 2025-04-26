import numpy as np
import copy as cp


# Wielomian w postaci Newtona wygląda tak:
# P(x) = c_0 + c_1*(x-x_0) + c_2*(x-x_0)*(x-x_1) + ...
# Gdzie x_0, x_1, ... to nasze węzły (np. te Czebyszewa),
# a c_0, c_1, c_2, ... to współczynniki, które musimy obliczyć - funkcja divdiff.
# # Mając już współczynniki c_k i węzły x_nodes, możemy obliczyć wartość wielomianu P(x) dla dowolnego nowego punktu x.
# Można by to zrobić podstawiając do wzoru Newtona, ale jest szybszy sposób,
# zwany schematem Hornera (a w tym przypadku Hornera-Newtona).

def cheb_nodes(a, b, n):
    """
    Oblicza 'n+1' węzłów Czebyszewa w przedziale [a, b].

    Argumenty:
        a (float): Początek przedziału.
        b (float): Koniec przedziału.
        n (int): Stopień wielomianu, który chcemy uzyskać.
                 Funkcja wygeneruje n+1 punktów (węzłów).

    Zwraca:
        numpy.ndarray: Tablica zawierająca obliczone węzły Czebyszewa.
    """
    # Tworzymy ciąg liczb całkowitych od 0 do n (łącznie n+1 liczb)
    # np.arange(n+1) da nam [0, 1, 2, ..., n]
    i = np.arange(n + 1)

    nodes = []
    for i in range(n + 1):
        # To jest wzór na węzły Czebyszewa.
        value = (a + b) / 2 + (b - a) / 2 * np.cos((2 * i + 1) * np.pi / (2 * n + 2))
        nodes.append(value)

    # Zwracamy obliczone węzły
    return nodes


def divdiff(x_nodes, y_values):
    """
    Oblicza współczynniki c_k wielomianu Newtona na podstawie
    węzłów x_nodes i odpowiadających im wartości funkcji y_values.

    Argumenty:
        x_nodes (numpy.ndarray): Tablica węzłów interpolacji (punkty na osi X).
        y_values (numpy.ndarray): Tablica wartości funkcji w tych węzłach (punkty na osi Y).
                                  Musi mieć tę samą długość co x_nodes.

    Zwraca:
        numpy.ndarray: Tablica współczynników c_k wielomianu Newtona.
                       Pierwszy element to c_0, drugi to c_1 itd.
    """
    # Sprawdzamy, czy mamy tyle samo x co y
    n = len(x_nodes)
    if len(y_values) != n:
        raise ValueError("Tablice x_nodes i y_values muszą mieć tę samą długość!")

    # Robimy kopię wartości y, żeby nie modyfikować oryginalnej tablicy.
    coeffs = cp.deepcopy(y_values)

    # Pętla obliczająca ilorazy różnicowe.
    # Zaczynamy od k=1, bo c_0 (czyli y_0) już mamy.
    for k in range(1, n):
        # Dla danego k aktualizujemy wartości c[i] od końca tablicy.
        for i in range(n - 1, k - 1, -1):
            # Iloraz różnicowy: (wartość z przodu - wartość z tyłu) / (odpowiednia różnica x-ów)
            coeffs[i] = (coeffs[i] - coeffs[i - 1]) / (x_nodes[i] - x_nodes[i - k])

    # Po zakończeniu pętli, tablica 'c' zawiera szukane współczynniki
    return coeffs


# P(x) = c_0 + c_1*(x-x_0) + c_2*(x-x_0)*(x-x_1) + ...

def newton(coeffs, x_nodes, x):
    """
    Oblicza wartość wielomianu w postaci Newtona w punkcie x,
    używając schematu Hornera-Newtona.

    Argumenty:
        coeffs (numpy.ndarray): Tablica współczynników c_k (wynik z divdiff).
        x_nodes (numpy.ndarray): Tablica węzłów interpolacji (użytych do obliczenia coeffs).
        x (float): Punkt (lub tablica punktów), w którym chcemy obliczyć wartość wielomianu.

    Zwraca:
        float lub numpy.ndarray: Wartość wielomianu P(x) w punkcie/punktach x.
    """
    # Zaczynamy od ostatniego współczynnika c_n
    # acc to 'akumulator', przechowuje wynik pośredni
    acc = coeffs[-1]  # coeffs[-1] to ostatni element tablicy

    # Iterujemy przez współczynniki i węzły od tyłu (oprócz ostatniego c_n i x_n).
    # coeffs[-2::-1] bierze elementy od przedostatniego do pierwszego (indeks 0), idąc wstecz.
    # x_nodes[-2::-1] bierze węzły od przedostatniego do pierwszego (indeks 0), idąc wstecz.
    # zip(A, B) łączy elementy z A i B w pary.
    # W pierwszej iteracji mamy (c_{n-1}, x_{n-1}), potem (c_{n-2}, x_{n-2}), itd. aż do (c_0, x_0).
    # ck to współczynnik, xk to węzeł.
    for ck, xk in zip(coeffs[-2::-1], x_nodes[-2::-1]):
        # To jest właśnie schemat Hornera-Newtona:
        # Wartość_poprzednia * (x - węzeł_k) + współczynnik_k
        # Rozwijając to od tyłu, dostajemy dokładnie wzór Newtona:
        # Krok 1: acc = c_n
        # Krok 2: acc = c_n * (x - x_{n-1}) + c_{n-1}
        # Krok 3: acc = (c_n * (x - x_{n-1}) + c_{n-1}) * (x - x_{n-2}) + c_{n-2}
        # ... i tak dalej, aż dojdziemy do c_0.
        acc = acc * (x - xk) + ck

    # Po zakończeniu pętli, 'acc' zawiera ostateczną wartość wielomianu P(x).
    return acc
