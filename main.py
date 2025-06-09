import pygame
import numpy as np

#Ustawienia
SZEROKOSC, WYSOKOSC = 1920, 1080
ROZMIAR_KOMORKI = 20
SIATKA_SZEROKOSC = SZEROKOSC // ROZMIAR_KOMORKI
SIATKA_WYSOKOSC = (WYSOKOSC - 150) // ROZMIAR_KOMORKI

SZYBKOSCI = [5, 10, 20]
NAZWY_PREDKOSCI = ["Wolno", "Normalnie", "Szybko"]
indeks_predkosci = 1
SZYBKOSC = SZYBKOSCI[indeks_predkosci]
CZARNY = (0, 0, 0)
BIALY = (255, 255, 255)
SZARY = (50, 50, 50)
KOLOR_PRZYCISKU = (70, 130, 180)
KOLOR_NAJECHANIA = (100, 160, 210)
KOLOR_TEKSTU = (255, 255, 255)

# Inicjalizacja
pygame.init()
ekran = pygame.display.set_mode((SZEROKOSC, WYSOKOSC))
pygame.display.set_caption("Gra w zycie")
zegar = pygame.time.Clock()
czcionka = pygame.font.SysFont(None, 28)

# Siatka
siatka = np.zeros((SIATKA_WYSOKOSC, SIATKA_SZEROKOSC), dtype=int)
symulacja = False

#Wzorce
wzorce = {
    "Brak": np.array([[1]]),
    "Glider": np.array([
        [0, 1, 0],
        [0, 0, 1],
        [1, 1, 1]
    ]),
    "Pulsar": np.array([
        [0,0,1,1,1,0,0,0,1,1,1,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,0],
        [1,0,0,0,0,1,0,1,0,0,0,0,1],
        [1,0,0,0,0,1,0,1,0,0,0,0,1],
        [1,0,0,0,0,1,0,1,0,0,0,0,1],
        [0,0,1,1,1,0,0,0,1,1,1,0,0]
    ]),
    "LWSS": np.array([
        [0,1,1,1,1],
        [1,0,0,0,1],
        [0,0,0,0,1],
        [1,0,0,1,0]
    ])
}
wybrany_wzorzec = "Brak"

class Przycisk:
    """
    Reprezentuje przycisk interfejsu graficznego.

    :param tekst: Tekst wyświetlany na przycisku.
    :type tekst: str
    :param x: Współrzędna X lewego górnego rogu.
    :type x: int
    :param y: Współrzędna Y lewego górnego rogu.
    :type y: int
    :param szer: Szerokość przycisku.
    :type szer: int
    :param wys: Wysokość przycisku.
    :type wys: int
    :param akcja: Funkcja wykonywana po kliknięciu przycisku.
    :type akcja: function
    """
    def __init__(self, tekst, x, y, szer, wys, akcja):
        self.prostokat = pygame.Rect(x, y, szer, wys)
        self.tekst = tekst
        self.akcja = akcja

    def rysuj(self, powierzchnia, pozycja_myszy):
        """
        Rysuje przycisk na ekranie.

        :param powierzchnia: Powierzchnia, na której rysujemy (np. ekran).
        :type powierzchnia: pygame.Surface
        :param pozycja_myszy: Aktualna pozycja myszy do sprawdzenia efektu najechania.
        :type pozycja_myszy: tuple[int, int]
        """
        kolor = KOLOR_NAJECHANIA if self.prostokat.collidepoint(pozycja_myszy) else KOLOR_PRZYCISKU
        pygame.draw.rect(powierzchnia, kolor, self.prostokat)
        pygame.draw.rect(powierzchnia, BIALY, self.prostokat, 2)
        etykieta = czcionka.render(self.tekst, True, KOLOR_TEKSTU)
        etykieta_rect = etykieta.get_rect(center=self.prostokat.center)
        powierzchnia.blit(etykieta, etykieta_rect)


def rysuj_siatke(powierzchnia, siatka):
    """
    Rysuje siatkę komórek na ekranie.

    :param powierzchnia: Powierzchnia do rysowania (np. ekran).
    :type powierzchnia: pygame.Surface
    :param siatka: Dwuwymiarowa tablica numpy z wartościami komórek (0 lub 1).
    :type siatka: numpy.ndarray
    """

    powierzchnia.fill(CZARNY)
    for y in range(SIATKA_WYSOKOSC):
        for x in range(SIATKA_SZEROKOSC):
            if siatka[y, x] == 1:
                pygame.draw.rect(powierzchnia, BIALY, (x * ROZMIAR_KOMORKI, y * ROZMIAR_KOMORKI, ROZMIAR_KOMORKI, ROZMIAR_KOMORKI))
    for x in range(0, SZEROKOSC, ROZMIAR_KOMORKI):
        pygame.draw.line(powierzchnia, SZARY, (x, 0), (x, SIATKA_WYSOKOSC * ROZMIAR_KOMORKI))
    for y in range(0, SIATKA_WYSOKOSC * ROZMIAR_KOMORKI, ROZMIAR_KOMORKI):
        pygame.draw.line(powierzchnia, SZARY, (0, y), (SZEROKOSC, y))

def aktualizuj_siatke(siatka):
    """
    Zwraca nową siatkę na podstawie obecnego stanu zgodnie z zasadami gry w życie.

    :param siatka: Aktualna siatka komórek.
    :type siatka: numpy.ndarray
    :return: Zaktualizowana siatka komórek.
    :rtype: numpy.ndarray
    """

    nowa_siatka = np.copy(siatka)
    for y in range(SIATKA_WYSOKOSC):
        for x in range(SIATKA_SZEROKOSC):
            sasiedzi = np.sum(siatka[max(0, y-1):min(y+2, SIATKA_WYSOKOSC), max(0, x-1):min(x+2, SIATKA_SZEROKOSC)]) - siatka[y, x]
            if siatka[y, x] == 1 and sasiedzi not in [2, 3]:
                nowa_siatka[y, x] = 0
            elif siatka[y, x] == 0 and sasiedzi == 3:
                nowa_siatka[y, x] = 1
    return nowa_siatka

def start():
    """
    Rozpoczyna symulację.
    """
    global symulacja
    symulacja = True

def stop():
    """
    Zatrzymuje symulację.
    """
    global symulacja
    symulacja = False

def wyczysc():
    """
    Czyści siatkę, ustawiając wszystkie komórki na 0 (martwe).
    """
    global siatka
    siatka = np.zeros((SIATKA_WYSOKOSC, SIATKA_SZEROKOSC), dtype=int)

def losuj():
    """
    Losowo wypełnia siatkę żywymi komórkami z prawdopodobieństwem 20%.
    """
    global siatka
    siatka = np.random.choice([0, 1], size=(SIATKA_WYSOKOSC, SIATKA_SZEROKOSC), p=[0.8, 0.2])

def zmien_predkosc():
    """
    Przełącza prędkość symulacji pomiędzy: Wolno, Normalnie, Szybko.
    """
    global indeks_predkosci, SZYBKOSC
    indeks_predkosci = (indeks_predkosci + 1) % len(SZYBKOSCI)
    SZYBKOSC = SZYBKOSCI[indeks_predkosci]

def wybierz_wzorzec(nazwa):
    """
    Ustawia aktualny wzorzec do wstawienia przy kliknięciu w siatkę.

    :param nazwa: Nazwa wzorca (musi istnieć w słowniku `wzorce`).
    :type nazwa: str
    """
    global wybrany_wzorzec
    wybrany_wzorzec = nazwa


# Przyciski główne
przyciski = [
    Przycisk("Start", 20, WYSOKOSC - 90, 90, 40, start),
    Przycisk("Stop", 120, WYSOKOSC - 90, 90, 40, stop),
    Przycisk("Wyczyść", 220, WYSOKOSC - 90, 90, 40, wyczysc),
    Przycisk("Losuj", 320, WYSOKOSC - 90, 90, 40, losuj),
    Przycisk("Szybkość", 420, WYSOKOSC - 90, 120, 40, zmien_predkosc),
]

# Przyciski wzorców
przyciski_wzorcow = [
    Przycisk("Brak", 20, WYSOKOSC - 45, 70, 35, lambda: wybierz_wzorzec("Brak")),
    Przycisk("Glider", 100, WYSOKOSC - 45, 90, 35, lambda: wybierz_wzorzec("Glider")),
    Przycisk("Pulsar", 200, WYSOKOSC - 45, 90, 35, lambda: wybierz_wzorzec("Pulsar")),
    Przycisk("LWSS", 300, WYSOKOSC - 45, 90, 35, lambda: wybierz_wzorzec("LWSS")),
]

#Pętla główna programu
dziala = True
while dziala:
    zegar.tick(SZYBKOSC)
    pozycja_myszy = pygame.mouse.get_pos()
    klikniecie = pygame.mouse.get_pressed()

    for zdarzenie in pygame.event.get():
        if zdarzenie.type == pygame.QUIT:
            dziala = False

        if zdarzenie.type == pygame.MOUSEBUTTONDOWN:
            mx, my = zdarzenie.pos

            for p in przyciski:
                if p.prostokat.collidepoint(mx, my):
                    p.akcja()

            for p in przyciski_wzorcow:
                if p.prostokat.collidepoint(mx, my):
                    p.akcja()

            if not symulacja and my < SIATKA_WYSOKOSC * ROZMIAR_KOMORKI:
                gx, gy = mx // ROZMIAR_KOMORKI, my // ROZMIAR_KOMORKI
                wzorzec = wzorce[wybrany_wzorzec]
                wysokosc_wz, szerokosc_wz = wzorzec.shape
                if gy + wysokosc_wz <= SIATKA_WYSOKOSC and gx + szerokosc_wz <= SIATKA_SZEROKOSC:
                    for dy in range(wysokosc_wz):
                        for dx in range(szerokosc_wz):
                            siatka[gy + dy, gx + dx] = wzorzec[dy, dx]

    if symulacja:
        siatka = aktualizuj_siatke(siatka)

    rysuj_siatke(ekran, siatka)
    for p in przyciski:
        p.rysuj(ekran, pozycja_myszy)
    for p in przyciski_wzorcow:
        p.rysuj(ekran, pozycja_myszy)

    tryb = czcionka.render(f"Tryb: {'Symulacja' if symulacja else 'Edycja'} | Szybkość: {NAZWY_PREDKOSCI[indeks_predkosci]}", True, KOLOR_TEKSTU )
    ekran.blit(tryb, (20, WYSOKOSC - 130))
    tekst_wzorca = czcionka.render(f"Wzorzec: {wybrany_wzorzec}", True, KOLOR_TEKSTU)
    ekran.blit(tekst_wzorca, (SZEROKOSC - 220, WYSOKOSC - 45))

    pygame.display.flip()

pygame.quit()
