"""
Interfejs graficzny dla systemu BrewSense - Wersja Responsywna (Naprawiona Skalowalność)
"""

import sys
import numpy as np
import matplotlib
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                              QHBoxLayout, QLabel, QSlider, QPushButton,
                              QFrame, QSplitter, QSizePolicy, QComboBox, QMessageBox, QDialog)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QPointF, QRectF, pyqtProperty
from PyQt5.QtGui import (QPainter, QColor, QPen, QBrush, QLinearGradient,
                         QRadialGradient, QPainterPath, QFont)

matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

# --- MOCK SYSTEMU ROZMYTEGO (Dla uruchomienia bez pliku fuzzy_system.py) ---
try:
    from fuzzy_system import CoffeeQualitySystem
except ImportError:
    class CoffeeQualitySystem:
        def evaluate(self, b, a, ar, t):
            # Prosta symulacja logiki dla testów
            score = 100 - (abs(5-b)*5 + abs(5-a)*5 + abs(90-t)*2)
            return max(0, min(100, score))
        def get_variables(self):
            # Mockowanie zmiennych do wykresów
            x = np.linspace(0, 10, 100)
            gauss = lambda x, m, s: np.exp(-((x - m) ** 2) / (2 * s ** 2))
            return {
                'bitterness': type('obj', (object,), {'universe': x, 'terms': {'low': type('o',(),{'mf': gauss(x, 2, 1)})(), 'medium': type('o',(),{'mf': gauss(x, 5, 1)})(), 'high': type('o',(),{'mf': gauss(x, 8, 1)})()}}),
                'acidity': type('obj', (object,), {'universe': x, 'terms': {'low': type('o',(),{'mf': gauss(x, 2, 1)})(), 'medium': type('o',(),{'mf': gauss(x, 5, 1)})(), 'high': type('o',(),{'mf': gauss(x, 8, 1)})()}}),
                'aroma': type('obj', (object,), {'universe': x, 'terms': {'weak': type('o',(),{'mf': gauss(x, 2, 1)})(), 'strong': type('o',(),{'mf': gauss(x, 8, 1)})()}}),
                'temperature': type('obj', (object,), {'universe': np.linspace(60, 100, 100), 'terms': {'optimum': type('o',(),{'mf': gauss(np.linspace(60, 100, 100), 90, 5)})()}}),
                'quality': type('obj', (object,), {'universe': np.linspace(0, 100, 100), 'terms': {'good': type('o',(),{'mf': gauss(np.linspace(0, 100, 100), 80, 10)})()}})
            }

# --- KONFIGURACJA ---
COLORS = {
    'background': '#F5F5DC', 'panel_left': '#E8DCC4', 'panel_middle': '#FFFFFF',
    'panel_right': '#FFF8E7', 'panel_bottom': '#D2B48C', 'button_primary': '#6F4E37',
    'text_dark': '#2F1E15', 'accent': '#CD853F'
}

COFFEE_PROFILES = {
    "Własny (Manualny)": {"desc": "Ręczne ustawienia.", "params": None},
    "Espresso Italiano": {"desc": "Klasyczne włoskie espresso.", "params": {"bitterness": 8.0, "acidity": 3.0, "aroma": 9.0, "temperature": 90.0}},
    "Americano": {"desc": "Espresso z wodą.", "params": {"bitterness": 4.5, "acidity": 4.0, "aroma": 6.0, "temperature": 94.0}},
    "Cappuccino": {"desc": "Balans mleka i kawy.", "params": {"bitterness": 3.5, "acidity": 2.5, "aroma": 7.0, "temperature": 70.0}},
    "Flat White": {"desc": "Podwójne espresso z mlekiem.", "params": {"bitterness": 6.0, "acidity": 3.5, "aroma": 8.0, "temperature": 75.0}},
    "Cold Brew": {"desc": "Kawa parzona na zimno.", "params": {"bitterness": 2.0, "acidity": 1.5, "aroma": 5.0, "temperature": 60.0}}
}

QSS_STYLE = """
QMainWindow { background-color: #F5F5DC; }
QFrame { border-radius: 10px; }
QLabel { color: #2F1E15; }
QPushButton {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #D2B48C, stop:1 #BC9A6B);
    color: #2F1E15; border: 2px solid #8B6F47; border-radius: 8px; padding: 8px 15px; font-weight: bold;
}
QPushButton:hover { background: #E8DCC4; }
QSlider::groove:horizontal { border: 1px solid #999; height: 8px; background: #CD853F; border-radius: 4px; }
QSlider::handle:horizontal { background: #6F4E37; border: 2px solid #2F1E15; width: 18px; margin: -6px 0; border-radius: 9px; }
"""

# --- WIDGETY ---

class CoffeeVisualizer(QWidget):
    """Widget wizualizacji kubka - WERSJA RESPONSYWNA"""

    def __init__(self, parent=None):
        super().__init__(parent)
        # Zmieniono z fixed 400x550 na mniejszy min size, żeby pozwolić na skalowanie w dół
        self.setMinimumSize(200, 250)
        self.quality_value = 0
        self.temperature_value = 60
        self.fill_level = 0

        self.animation = QPropertyAnimation(self, b"fillLevel")
        self.animation.setDuration(800)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)

    @pyqtProperty(float)
    def fillLevel(self): return self.fill_level

    @fillLevel.setter
    def fillLevel(self, value):
        self.fill_level = value
        self.update()

    def set_coffee(self, quality, temperature):
        self.quality_value = quality
        self.temperature_value = temperature
        target_fill = quality / 100.0
        self.animation.stop()
        self.animation.setStartValue(float(self.fill_level))
        self.animation.setEndValue(float(target_fill))
        self.animation.start()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # 1. Rysuj tło na całym dostępnym obszarze
        painter.fillRect(self.rect(), QColor(COLORS['panel_right']))

        # 2. LOGIKA SKALOWANIA (KLUCZ DO NAPRAWY)
        # Oryginalny kod rysował na sztywno dla wymiarów ok. 400x550.
        # Definiujemy to jako nasz "Base Size".
        BASE_W, BASE_H = 400.0, 550.0

        # Obliczamy skalę, aby zachować proporcje
        scale_x = self.width() / BASE_W
        scale_y = self.height() / BASE_H
        scale = min(scale_x, scale_y) * 0.95 # 0.95 dla marginesu

        # Przesuwamy środek układu współrzędnych na środek widgetu
        painter.translate(self.width() / 2, self.height() / 2)
        # Skalujemy
        painter.scale(scale, scale)
        # Przesuwamy "wirtualny" początek z powrotem, aby oryginalne koordynaty działały
        painter.translate(-BASE_W / 2, -BASE_H / 2)

        # --- Poniżej oryginalna logika rysowania, ale teraz jest ona automatycznie skalowana ---

        center_x = BASE_W // 2
        cup_bottom_y = 400
        cup_top_y = 180
        cup_height = cup_bottom_y - cup_top_y
        cup_bottom_width = 140
        cup_top_width = 160
        spodek_y = 420

        left_bottom = center_x - cup_bottom_width // 2
        right_bottom = center_x + cup_bottom_width // 2
        left_top = center_x - cup_top_width // 2
        right_top = center_x + cup_top_width // 2

        # Cień
        shadow_gradient = QRadialGradient(center_x, spodek_y + 16, 95)
        shadow_gradient.setColorAt(0, QColor(0, 0, 0, 60))
        shadow_gradient.setColorAt(1, QColor(0, 0, 0, 0))
        painter.setBrush(QBrush(shadow_gradient))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(QPointF(center_x, spodek_y + 16), 95, 12)

        # Spodek
        painter.setPen(QPen(QColor(COLORS['text_dark']), 2))
        saucer_gradient = QLinearGradient(0, spodek_y, 0, spodek_y + 20)
        saucer_gradient.setColorAt(0, QColor(COLORS['accent']).lighter(110))
        saucer_gradient.setColorAt(1, QColor(COLORS['accent']).darker(110))
        painter.setBrush(QBrush(saucer_gradient))
        painter.drawEllipse(QPointF(center_x, spodek_y + 10), 95, 10)

        # Korpus kubka
        cup_path = QPainterPath()
        cup_path.moveTo(left_top, cup_top_y)
        cup_path.lineTo(right_top, cup_top_y)
        cup_path.lineTo(right_bottom, cup_bottom_y)
        cup_path.lineTo(left_bottom, cup_bottom_y)
        cup_path.closeSubpath()

        cup_gradient = QLinearGradient(left_top, cup_top_y, right_top, cup_top_y)
        cup_gradient.setColorAt(0, QColor(COLORS['panel_right']).darker(105))
        cup_gradient.setColorAt(0.5, QColor(COLORS['panel_right']).lighter(105))
        cup_gradient.setColorAt(1, QColor(COLORS['panel_right']).darker(105))

        painter.setPen(QPen(QColor(COLORS['text_dark']), 3))
        painter.setBrush(QBrush(cup_gradient))
        painter.drawPath(cup_path)

        # Uchwyt
        handle_path = QPainterPath()
        handle_x = right_top + 10
        handle_y_top = cup_top_y + 30
        handle_y_bottom = cup_top_y + 120
        handle_path.moveTo(handle_x, handle_y_top)
        handle_path.cubicTo(handle_x + 50, handle_y_top, handle_x + 50, handle_y_bottom, handle_x, handle_y_bottom)
        painter.setPen(QPen(QColor(COLORS['text_dark']), 3))
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(handle_path)

        # Płyn (Kawa)
        if self.fill_level > 0:
            coffee_color = self._get_coffee_color(self.quality_value)
            coffee_level = cup_bottom_y - (cup_height * self.fill_level * 0.85)
            coffee_width_ratio = (coffee_level - cup_top_y) / cup_height
            coffee_left = left_top + (left_bottom - left_top) * coffee_width_ratio
            coffee_right = right_top + (right_bottom - right_top) * coffee_width_ratio

            coffee_path = QPainterPath()
            coffee_path.moveTo(coffee_left, coffee_level)
            coffee_path.lineTo(coffee_right, coffee_level)
            coffee_path.lineTo(right_bottom, cup_bottom_y)
            coffee_path.lineTo(left_bottom, cup_bottom_y)
            coffee_path.closeSubpath()

            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(QColor(coffee_color)))
            painter.drawPath(coffee_path)

            painter.setBrush(QBrush(QColor(coffee_color).darker(110)))
            painter.drawEllipse(QPointF(center_x, coffee_level), (coffee_right - coffee_left) / 2, 8)

        # Para
        if self.temperature_value > 75:
            self._draw_steam(painter, center_x, cup_top_y - 10)

        # Teksty (również się skalują dzięki transformacji)
        painter.setPen(QPen(QColor(COLORS['text_dark']), 1))
        font = QFont("Segoe UI", 20, QFont.Bold)
        painter.setFont(font)
        painter.drawText(QRectF(0, 460, BASE_W, 30), Qt.AlignCenter, f"{self.quality_value:.1f}/100")

        font.setPointSize(14)
        painter.setFont(font)
        painter.drawText(QRectF(0, 490, BASE_W, 30), Qt.AlignCenter, self._get_quality_label(self.quality_value))

    # --- Metody pomocnicze (bez zmian logicznych) ---
    def _draw_steam(self, painter, cx, sy):
        painter.setPen(QPen(QColor(200, 200, 200, 100), 3))
        path = QPainterPath()
        path.moveTo(cx, sy)
        path.lineTo(cx, sy - 40)
        painter.drawPath(path)

    def _get_coffee_color(self, v): return "#6F4E37" if v > 50 else "#8B6F47"
    def _get_quality_label(self, v): return "Dobra" if v > 50 else "Słaba"


class MplCanvas(FigureCanvasQTAgg):
    """Canvas matplotlib - WERSJA RESPONSYWNA"""
    def __init__(self, parent=None, width=5, height=4, dpi=90): # Zmieniono width/height na mniejsze
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.fig.patch.set_facecolor('#FFFFFF')
        super().__init__(self.fig)
        self.setParent(parent)
        # Kluczowe: Pozwalamy wykresowi się kurczyć i rozszerzać
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.updateGeometry()

        self.axes = [self.fig.add_subplot(5, 1, i+1) for i in range(5)]
        self.fig.tight_layout(pad=1.0) # Mniejszy padding


class ProgressBarWidget(QWidget):
    """Pasek postępu"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(40) # Mniejsza minimalna wysokość
        self.progress_value = 0
        self.animation = QPropertyAnimation(self, b"progressValue")
        self.animation.setDuration(800)

    @pyqtProperty(float)
    def progressValue(self): return self.progress_value
    @progressValue.setter
    def progressValue(self, value):
        self.progress_value = value
        self.update()

    def set_progress(self, value):
        self.animation.stop()
        self.animation.setStartValue(float(self.progress_value))
        self.animation.setEndValue(float(value))
        self.animation.start()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor("#CCCCCC"))
        fill_w = int((self.progress_value / 100.0) * self.width())
        if fill_w > 0:
            painter.fillRect(0, 0, fill_w, self.height(), QColor(COLORS['button_primary']))


class CoffeeGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BrewSense - System Oceny Jakości Kawy")
        # Zmieniono geometry: Zamiast 1920x1080 (co może wychodzić poza ekran),
        # używamy bezpieczniejszego rozmiaru, np. 1200x800
        self.resize(1200, 800)

        self.fuzzy_system = CoffeeQualitySystem()
        self.current_quality = 0
        self.setStyleSheet(QSS_STYLE)
        self._create_widgets()

    def _create_widgets(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)

        # Splitter pozwala użytkownikowi zmieniać rozmiar paneli
        top_splitter = QSplitter(Qt.Horizontal)

        # Lewy panel (ScrollArea byłoby tu opcją, ale spróbujmy zmieścić w Frame)
        left_panel = self._create_left_panel()
        top_splitter.addWidget(left_panel)

        # Środkowy panel (Wykresy)
        middle_panel = self._create_middle_panel()
        top_splitter.addWidget(middle_panel)

        # Prawy panel (Wizualizacja)
        right_panel = self._create_right_panel()
        top_splitter.addWidget(right_panel)

        # Ustawiamy zachowanie przy zmianie rozmiaru
        top_splitter.setStretchFactor(0, 2)
        top_splitter.setStretchFactor(1, 5) # Wykresy dostają najwięcej miejsca
        top_splitter.setStretchFactor(2, 3)
        top_splitter.setCollapsible(0, False) # Nie pozwalaj zwinąć panelu sterowania

        main_layout.addWidget(top_splitter, stretch=10)

        bottom_panel = self._create_bottom_panel()
        main_layout.addWidget(bottom_panel, stretch=1)

    def _create_left_panel(self):
        panel = QFrame()
        panel.setStyleSheet(f"background-color: {COLORS['panel_left']};")
        layout = QVBoxLayout(panel)

        title = QLabel("Parametry Kawy")
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        layout.addWidget(title, alignment=Qt.AlignCenter)

        # Combo Profilu
        self.profile_combo = QComboBox()
        self.profile_combo.addItems(COFFEE_PROFILES.keys())
        self.profile_combo.currentTextChanged.connect(self.load_profile)
        layout.addWidget(QLabel("Wybierz profil:"))
        layout.addWidget(self.profile_combo)

        # Opis
        self.profile_desc = QLabel("Ręczne ustawienia.")
        self.profile_desc.setWordWrap(True)
        self.profile_desc.setStyleSheet("font-style: italic; font-size: 10pt;")
        layout.addWidget(self.profile_desc)

        # Suwaki
        self.bitterness_slider, self.bitterness_lbl = self._create_slider(layout, "Gorzkość", 0, 100, 50)
        self.acidity_slider, self.acidity_lbl = self._create_slider(layout, "Kwasowość", 0, 100, 50)
        self.aroma_slider, self.aroma_lbl = self._create_slider(layout, "Aromat", 0, 100, 50)
        self.temperature_slider, self.temp_lbl = self._create_slider(layout, "Temp", 600, 950, 800, is_temp=True)

        layout.addStretch()

        btn_layout = QHBoxLayout()
        eval_btn = QPushButton("Oceń")
        eval_btn.clicked.connect(self.evaluate_coffee)
        rst_btn = QPushButton("Reset")
        rst_btn.clicked.connect(self.reset_values)
        btn_layout.addWidget(eval_btn)
        btn_layout.addWidget(rst_btn)
        layout.addLayout(btn_layout)

        return panel

    def _create_slider(self, parent_layout, text, min_v, max_v, def_v, is_temp=False):
        lbl = QLabel(text)
        slider = QSlider(Qt.Horizontal)
        slider.setRange(min_v, max_v)
        slider.setValue(def_v)

        val_lbl = QLabel(f"{def_v/10:.1f}{'°C' if is_temp else ''}")
        val_lbl.setFixedWidth(50)

        slider.valueChanged.connect(lambda v: val_lbl.setText(f"{v/10:.1f}{'°C' if is_temp else ''}"))

        h_layout = QHBoxLayout()
        h_layout.addWidget(slider)
        h_layout.addWidget(val_lbl)

        parent_layout.addWidget(lbl)
        parent_layout.addLayout(h_layout)
        return slider, val_lbl

    def _create_middle_panel(self):
        panel = QFrame()
        panel.setStyleSheet(f"background-color: {COLORS['panel_middle']};")
        layout = QVBoxLayout(panel)
        # Zmniejszone marginesy dla oszczędności miejsca
        layout.setContentsMargins(5, 5, 5, 5)

        self.plot_canvas = MplCanvas(panel)
        layout.addWidget(self.plot_canvas)
        return panel

    def _create_right_panel(self):
        panel = QFrame()
        panel.setStyleSheet(f"background-color: {COLORS['panel_right']};")
        layout = QVBoxLayout(panel)

        self.visualizer = CoffeeVisualizer()
        # Dodajemy visualizer z Expanding policy
        self.visualizer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self.visualizer)
        return panel

    def _create_bottom_panel(self):
        panel = QFrame()
        panel.setStyleSheet(f"background-color: {COLORS['panel_bottom']};")
        panel.setMaximumHeight(80) # Mniejszy panel dolny
        layout = QHBoxLayout(panel)

        self.result_lbl = QLabel("Wynik: 0.0")
        self.result_lbl.setFont(QFont("Segoe UI", 18, QFont.Bold))
        layout.addWidget(self.result_lbl)

        self.progress = ProgressBarWidget()
        layout.addWidget(self.progress)

        # Dodatkowy przycisk wyjaśnienia
        info_btn = QPushButton("?")
        info_btn.setFixedWidth(40)
        info_btn.clicked.connect(self.show_explanation_dialog)
        layout.addWidget(info_btn)

        return panel

    def load_profile(self, name):
        p = COFFEE_PROFILES[name]
        self.profile_desc.setText(p['desc'])
        if p['params']:
            self.bitterness_slider.setValue(int(p['params']['bitterness']*10))
            self.acidity_slider.setValue(int(p['params']['acidity']*10))
            self.aroma_slider.setValue(int(p['params']['aroma']*10))
            self.temperature_slider.setValue(int(p['params']['temperature']*10))
            self.evaluate_coffee()

    def reset_values(self):
        self.profile_combo.setCurrentIndex(0)
        self.bitterness_slider.setValue(50)
        self.acidity_slider.setValue(50)
        self.aroma_slider.setValue(50)
        self.temperature_slider.setValue(800)
        self.visualizer.clear()
        self.progress.set_progress(0)
        self._clear_plots()

    def evaluate_coffee(self):
        b = self.bitterness_slider.value() / 10.0
        a = self.acidity_slider.value() / 10.0
        ar = self.aroma_slider.value() / 10.0
        t = self.temperature_slider.value() / 10.0

        quality = self.fuzzy_system.evaluate(b, a, ar, t)
        self.current_quality = quality

        self.result_lbl.setText(f"Wynik: {quality:.1f}")
        self.visualizer.set_coffee(quality, t)
        self.progress.set_progress(quality)
        self._update_plots(b, a, ar, t, quality)

    def _clear_plots(self):
        for ax in self.plot_canvas.axes:
            ax.clear()
            ax.grid(alpha=0.3)
        self.plot_canvas.draw()

    def _update_plots(self, b, a, ar, t, q):
        vars = self.fuzzy_system.get_variables()
        inputs = [b, a, ar, t, q]
        keys = ['bitterness', 'acidity', 'aroma', 'temperature', 'quality']
        titles = ['Gorzkość', 'Kwasowość', 'Aromat', 'Temperatura', 'Jakość']

        for i, ax in enumerate(self.plot_canvas.axes):
            ax.clear()
            var = vars[keys[i]]
            for name, term in var.terms.items():
                ax.plot(var.universe, term.mf, label=name)

            ax.axvline(inputs[i], color='k', linestyle='--')
            ax.set_title(titles[i], fontsize=8)
            ax.tick_params(labelsize=6)
            # Usuwamy legendę, jeśli zasłania za dużo w małym oknie
            # ax.legend(fontsize=6)

        self.plot_canvas.fig.tight_layout()
        self.plot_canvas.draw()

    def show_explanation_dialog(self):
        QMessageBox.information(self, "Raport", f"Obecna ocena jakości kawy to {self.current_quality:.1f}/100.")

def main():
    """Funkcja główna"""
    app = QApplication(sys.argv)
    window = CoffeeGUI()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()