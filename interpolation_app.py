# --- Importy niezbędnych bibliotek ---
import matplotlib.pyplot as plt  # Biblioteka do tworzenia wykresów
import numpy as np  # Biblioteka do obliczeń numerycznych, głównie na tablicach
import streamlit as st  # Główna biblioteka do tworzenia aplikacji webowych
import pandas as pd # Biblioteka do obsługi danych, np. wczytywania CSV
import io # Do obsługi strumieni danych, np. z przesłanego pliku

# Import funkcji obliczeniowych z lokalnego pliku newton.py, horner.py
try:
    from newton import cheb_nodes, divdiff, newton
    from horner import horner
except ImportError:
    st.error(
        "Nie można zaimportować funkcji z pliku `newton.py` lub `horner.py`. Upewnij się, że pliki istnieją i są w tym samym folderze.")
    st.stop()  # Zatrzymuje wykonywanie skryptu

# --- Definicje funkcji matematycznych do interpolacji ---
FUNKCJE = {
    "2x - 1": {
        "f": lambda x: 2 * x - 1,
        "latex_str": r"2x - 1",
        "is_polynomial": True,
        "coeffs": [2.0, -1.0]
    },
    "|x|": {
        "f": lambda x: np.abs(x),
        "latex_str": r"|x|",
        "is_polynomial": False
    },
    "x^4 - 3x^2 + x - 2": {
        "f": lambda x: x ** 4 - 3 * x ** 2 + x - 2,
        "latex_str": r"x^4 - 3x^2 + x - 2",
        "is_polynomial": True,
        "coeffs": [1.0, 0.0, -3.0, 1.0, -2.0]
    },
    "cos(2x) + sin(x)": {
        "f": lambda x: np.cos(2 * x) + np.sin(x),
        "latex_str": r"\cos(2x) + \sin(x)",
        "is_polynomial": False
    },
    "e^|x-1| - 2": {
        "f": lambda x: np.exp(np.abs(x - 1.0)) - 2.0,
        "latex_str": r"e^{|x-1|} - 2",
        "is_polynomial": False
    },
    "1/(1+25*x^2)": {
        "f": lambda x: 1 / (1 + (25 * x ** 2)),
        "latex_str": r"\frac{1}{1+25x^2}",
        "is_polynomial": False
    },
}

# --- Funkcja do parsowania wczytanego pliku ---
def parse_uploaded_file(uploaded_file):
    """Parsuje wczytany plik (CSV/TXT) do tablic x_nodes i y_nodes."""
    try:
        # Odczytaj zawartość pliku jako tekst
        string_data = uploaded_file.getvalue().decode("utf-8")
        # Zakładamy brak nagłówka (header=None) i traktujemy białe znaki jako separatory
        try:
            data = pd.read_csv(io.StringIO(string_data), header=None, sep='\\s+', names=['x', 'y'], dtype=np.float64)
        except Exception:
            # Jeśli białe znaki zawiodą, spróbuj przecinka
            data = pd.read_csv(io.StringIO(string_data), header=None, sep=',', names=['x', 'y'], dtype=np.float64)

        # czy mamy dwie kolumny
        if data.shape[1] != 2:
            st.error(f"Błąd parsowania: Oczekiwano 2 kolumn danych (x, y), znaleziono {data.shape[1]}.")
            return None, None

        # czy mamy co najmniej 2 punkty (potrzebne do interpolacji stopnia >= 1)
        if len(data) < 2:
            st.error(f"Błąd parsowania: Znaleziono tylko {len(data)} punkt(ów). Potrzebne są co najmniej 2 punkty do interpolacji.")
            return None, None

        # Usuń wiersze z brakującymi wartościami (NaN)
        data.dropna(inplace=True)
        if len(data) < 2:
            st.error(f"Błąd parsowania: Po usunięciu wierszy z brakującymi danymi zostało mniej niż 2 punkty.")
            return None, None

        # Sortowanie danych względem x
        data.sort_values(by='x', inplace=True)

        # Konwertuj do tablic NumPy
        x_nodes = data['x'].to_numpy()
        y_nodes = data['y'].to_numpy()

        # Sprawdź unikalność węzłów x
        if len(np.unique(x_nodes)) != len(x_nodes):
            st.warning("Uwaga: Wczytane węzły 'x' nie są unikalne. Może to prowadzić do problemów numerycznych.")

        return x_nodes, y_nodes

    except pd.errors.ParserError as pe:
        st.error(f"Błąd parsowania pliku: Nie można przetworzyć danych. Sprawdź format pliku. Szczegóły: {pe}")
        return None, None
    except ValueError as ve:
        st.error(f"Błąd konwersji danych: Upewnij się, że plik zawiera tylko wartości liczbowe. Szczegóły: {ve}")
        return None, None
    except Exception as e:
        st.error(f"Niespodziewany błąd podczas przetwarzania pliku: {e}")
        return None, None

# --- Główna część interfejsu Streamlit ---

st.title("Interaktywna Interpolacja Wielomianowa Newtona")

# --- Panel boczny (Sidebar) na ustawienia ---
st.sidebar.header("Ustawienia Interpolacji")

# 1. Wybór źródła danych
data_source = st.sidebar.radio(
    "Wybierz źródło danych:",
    ("Wybierz funkcję", "Wczytaj węzły z pliku"),
    key="data_source_selector" # Klucz, aby stan był pamiętany
)

# Inicjalizacja zmiennych
x_nodes, y_nodes = None, None
f = None
latex_representation = ""
plot_original_function = False
a, b = -5.0, 5.0 # Domyślne wartości, mogą zostać nadpisane
n_degree = 1 # Domyślny stopień

# --- Konfiguracja w zależności od źródła danych ---

if data_source == "Wybierz funkcję":
    plot_original_function = True #Flag do rysowania oryginalnej funkcji
    st.sidebar.subheader("Parametry funkcji")
    # Wybór funkcji
    selected_func_name = st.sidebar.radio(
        "Wybierz funkcję do interpolacji:",
        list(FUNKCJE.keys())
    )
    selected_func_details = FUNKCJE[selected_func_name]
    f = selected_func_details["f"]
    latex_representation = selected_func_details["latex_str"]

    # Wybór przedziału
    col1, col2 = st.sidebar.columns(2)
    with col1:
        a = st.number_input("a (początek)", value=-5.0, step=0.5, format="%.2f")
    with col2:
        b = st.number_input("b (koniec)", value=5.0, step=0.5, format="%.2f")

    if a >= b:
        st.sidebar.error("Wartość 'a' musi być mniejsza niż 'b'.")
        st.stop()

    # Wybór stopnia wielomianu
    n_degree = st.sidebar.slider("Stopień wielomianu interpolacyjnego (n):", min_value=1, max_value=50, value=5, step=1)
    num_nodes = n_degree + 1
    st.sidebar.write(f"Liczba węzłów Czebyszewa: {num_nodes}")

    # Obliczenie węzłów i wartości dla wybranej funkcji
    x_nodes = np.array(cheb_nodes(a, b, n_degree))
    if selected_func_details["is_polynomial"]:
        y_nodes = horner(x_nodes, selected_func_details["coeffs"])
    else:
        y_nodes = f(x_nodes)

elif data_source == "Wczytaj węzły z pliku":
    plot_original_function = False
    st.sidebar.subheader("Wczytywanie danych")
    uploaded_file = st.sidebar.file_uploader(
        "Wybierz plik CSV lub TXT",
        type=['csv', 'txt'],
        help="Plik powinien zawierać dwie kolumny (wartości x i y) oddzielone spacją, przecinkiem lub tabulatorem. Bez nagłówka."
    )

    if uploaded_file is not None:
        # Parsowanie pliku
        x_nodes, y_nodes = parse_uploaded_file(uploaded_file)

        if x_nodes is not None and y_nodes is not None:
            # Ustalenie stopnia na podstawie liczby punktów
            n_degree = len(x_nodes) - 1
            num_nodes = len(x_nodes)
            st.sidebar.write(f"Wczytano {num_nodes} węzłów.")
            st.sidebar.write(f"Stopień wynikowego wielomianu: n = {n_degree}")
            # Ustalenie przedziału rysowania na podstawie danych
            a = np.min(x_nodes)
            b = np.max(x_nodes)
            # Mały margines, jeśli a==b (mało prawdopodobne po walidacji)
            if np.isclose(a, b):
                a -= 0.5
                b += 0.5
    else:
        st.info("Proszę wczytać plik z danymi (x, y), aby kontynuować.")
        st.stop() # Zatrzymaj, jeśli nie ma pliku

# --- Obliczenia Interpolacji (jeśli mamy dane) ---

if x_nodes is not None and y_nodes is not None:
    # Wyświetlenie informacji w głównej części
    if plot_original_function:
        st.subheader(f"Interpolacja funkcji: ${latex_representation}$")
        st.write(f"Przedział interpolacji: [{a:.2f}, {b:.2f}]")
        st.write(f"Użyto {len(x_nodes)} węzłów Czebyszewa (stopień wielomianu n={n_degree}).")
    else:
        st.subheader("Interpolacja na podstawie wczytanych danych")
        st.write(f"Przedział danych x: [{a:.2f}, {b:.2f}]")
        st.write(f"Liczba wczytanych węzłów: {len(x_nodes)} (stopień wielomianu n={n_degree}).")


    # Blok try-except dla obliczeń i rysowania
    try:
        # 1. Obliczenie współczynników Newtona
        coeffs = divdiff(x_nodes, y_nodes)

        # 2. Wygenerowanie punktów do rysowania gładkiego wielomianu
        x_plot = np.linspace(a, b, 400)
        y_interpolated_plot = newton(coeffs, x_nodes, x_plot)

        # 3. Obliczenie wartości oryginalnej funkcji 
        y_original_plot = None
        if plot_original_function:
            if FUNKCJE[selected_func_name]["is_polynomial"]:
                 y_original_plot = horner(x_plot, FUNKCJE[selected_func_name]["coeffs"])
            else:
                 y_original_plot = f(x_plot)


        # --- Rysowanie Wykresu ---
        fig, ax = plt.subplots(figsize=(10, 6))

        # Rysowanie oryginalnej funkcji (jeśli dotyczy)
        if plot_original_function and y_original_plot is not None:
            ax.plot(x_plot, y_original_plot, label='Oryginalna funkcja', linestyle='--', color='blue')

        # Rysowanie wielomianu interpolacyjnego
        ax.plot(x_plot, y_interpolated_plot, label=f'Wielomian Newtona (st. n={n_degree})', color='green')

        # Zaznaczenie węzłów
        node_label = f'Węzły Czebyszewa ({len(x_nodes)})' if plot_original_function else f'Węzły z pliku ({len(x_nodes)})'
        ax.scatter(x_nodes, y_nodes, color='red', label=node_label, zorder=5)

        # --- Dynamiczne ustalanie zakresu osi Y ---
        # Zbierz wszystkie dane Y, które będą na wykresie
        all_y_on_plot = []
        if plot_original_function and y_original_plot is not None:
            all_y_on_plot.append(y_original_plot[np.isfinite(y_original_plot)])
        all_y_on_plot.append(y_interpolated_plot[np.isfinite(y_interpolated_plot)])
        all_y_on_plot.append(y_nodes[np.isfinite(y_nodes)]) # Dodaj y węzłów

        # Usuń puste tablice po filtrowaniu NaN/inf
        valid_y_arrays = [arr for arr in all_y_on_plot if len(arr) > 0]

        if valid_y_arrays:
            # Połącz wszystkie poprawne wartości Y
            all_valid_y = np.concatenate(valid_y_arrays)
            if len(all_valid_y) > 0:
                y_min_auto = np.min(all_valid_y)
                y_max_auto = np.max(all_valid_y)
                margin = (y_max_auto - y_min_auto) * 0.1 if y_max_auto > y_min_auto else 1.0
                ax.set_ylim(y_min_auto - margin, y_max_auto + margin)
            else:
                st.warning("Nie udało się ustalić zakresu osi Y (brak poprawnych danych po konkatenacji).")
        else:
            st.warning("Nie udało się ustalić zakresu osi Y (brak jakichkolwiek poprawnych danych).")


        # Etykiety, tytuł, legenda, siatka
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        title = "Porównanie funkcji i wielomianu interpolacyjnego" if plot_original_function else "Wielomian interpolacyjny dla wczytanych danych"
        ax.set_title(title)
        ax.legend()
        ax.grid(True)

        # Wyświetlenie wykresu
        st.pyplot(fig)

    # Obsługa błędów obliczeń/rysowania
    except ValueError as ve:
        st.error(f"Błąd wartości podczas obliczeń: {ve}")
        st.warning("Sprawdź, czy dane wejściowe są poprawne (np. unikalne węzły x dla 'divdiff').")
    except Exception as e:
        st.error(f"Wystąpił nieoczekiwany błąd podczas obliczeń lub rysowania: {e}")

else:
    # Komunikat, jeśli dane nie zostały jeszcze wczytane/wygenerowane
    # (Szczególnie istotne przy starcie aplikacji z wybraną opcją pliku)
    if data_source == "Wczytaj węzły z pliku":
         st.info("Proszę wczytać plik z danymi (x, y) w panelu bocznym.")
    # else: (dla 'Wybierz funkcję' domyślne wartości powinny zadziałać od razu)