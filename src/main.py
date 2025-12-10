"""
BrewSense - System Oceny Jakości Kawy
Punkt wejścia aplikacji
"""

from gui import CoffeeGUI


def main():
    """Funkcja główna uruchamiająca aplikację"""
    app = CoffeeGUI()
    app.run()


if __name__ == "__main__":
    main()