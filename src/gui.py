"""
Interfejs graficzny dla systemu BrewSense - wersja PyQt5
Implementacja GUI z zaawansowaną wizualizacją kubka i wykresami

"""

from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                              QHBoxLayout, QLabel, QSlider, QPushButton, 
                              QFrame, QGridLayout, QSplitter, QSizePolicy)
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QPointF, QRectF, pyqtProperty
from PyQt5.QtGui import (QPainter, QColor, QPen, QBrush, QLinearGradient, 
                         QRadialGradient, QPainterPath, QFont, QPalette, QIcon)
import sys
import numpy as np
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                              QHBoxLayout, QLabel, QSlider, QPushButton,
                              QFrame, QGridLayout, QSplitter, QSizePolicy,
                              QComboBox, QMessageBox)

try:
    from fuzzy_system import CoffeeQualitySystem
except ImportError:
    class CoffeeQualitySystem:
        """Dummy class for testing"""
        def evaluate(self, b, a, ar, t): return 75.0
        def get_variables(self): 
            return {
                'bitterness': type('obj', (object,), {'universe': np.arange(0, 10.1, 0.1), 'terms': {'low': type('obj', (object,), {'mf': np.zeros(101)})()}}),
                'acidity': type('obj', (object,), {'universe': np.arange(0, 10.1, 0.1), 'terms': {'low': type('obj', (object,), {'mf': np.zeros(101)})()}}),
                'aroma': type('obj', (object,), {'universe': np.arange(0, 10.1, 0.1), 'terms': {'weak': type('obj', (object,), {'mf': np.zeros(101)})()}}),
                'temperature': type('obj', (object,), {'universe': np.arange(60, 95.1, 0.1), 'terms': {'low': type('obj', (object,), {'mf': np.zeros(351)})()}}),
                'quality': type('obj', (object,), {'universe': np.arange(0, 100.1, 0.1), 'terms': {'very_poor': type('obj', (object,), {'mf': np.zeros(1001)})()}})
            }
        def get_quality_label(self, q): return "Bardzo dobra"


# Paleta kolorów (ciepła, kawowa)
COLORS = {
    'background': '#F5F5DC',      # Beżowy
    'panel_left': '#E8DCC4',      # Jasny brąz
    'panel_middle': '#FFFFFF',    # Biały
    'panel_right': '#FFF8E7',     # Kremowy
    'panel_bottom': '#D2B48C',    # Tan
    'button_primary': '#6F4E37',  # Brąz kawowy
    'button_secondary': '#8B4513',# Sienna
    'text_dark': '#2F1E15',       # Ciemny brąz
    'accent': '#CD853F',          # Peru
}

# Predefiniowane profile kawy z opisem (Why chosen) i parametrami
COFFEE_PROFILES = {
    "Własny (Manualny)": {
        "desc": "Ręczne ustawienia parametrów przez użytkownika.",
        "params": None
    },
    "Espresso Italiano": {
        "desc": "Klasyczne włoskie espresso. Mała objętość, wysoka intensywność i gęsta crema.",
        "params": {"bitterness": 8.0, "acidity": 3.0, "aroma": 9.0, "temperature": 90.0}
    },
    "Americano": {
        "desc": "Espresso przedłużone gorącą wodą. Łagodniejszy smak, wyższa temperatura serwowania.",
        "params": {"bitterness": 4.5, "acidity": 4.0, "aroma": 6.0, "temperature": 94.0}
    },
    "Cappuccino": {
        "desc": "Balans między kawą a spienionym mlekiem. Niższa temperatura i łagodniejsza gorycz.",
        "params": {"bitterness": 3.5, "acidity": 2.5, "aroma": 7.0, "temperature": 70.0}
    },
    "Flat White": {
        "desc": "Podwójne espresso z mlekiem. Wyższa intensywność niż Latte, aksamitna tekstura.",
        "params": {"bitterness": 6.0, "acidity": 3.5, "aroma": 8.0, "temperature": 75.0}
    },
    "Cold Brew": {
        "desc": "Kawa parzona na zimno. Bardzo niska kwasowość, specyficzny profil smakowy.",
        "params": {"bitterness": 2.0, "acidity": 1.5, "aroma": 5.0, "temperature": 60.0} # Min slidera to 60
    }
}

# Style QSS dla profesjonalnego wyglądu
QSS_STYLE = """
QMainWindow {
    background-color: #F5F5DC;
}

QFrame {
    border-radius: 10px;
}

QLabel {
    color: #2F1E15;
}

QPushButton {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #D2B48C, stop:0.5 #C4A484, stop:1 #BC9A6B);
    color: #2F1E15;
    border: 2px solid #8B6F47;
    border-radius: 8px;
    padding: 12px 30px;
    font-size: 14px;
    font-weight: bold;
}

QPushButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #E8DCC4, stop:0.5 #D2B48C, stop:1 #C4A484);
    border: 2px solid #6F4E37;
}

QPushButton:pressed {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #BC9A6B, stop:0.5 #A67C52, stop:1 #8B6F47);
    border: 2px solid #4A3728;
}

QPushButton#resetButton {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #C4A484, stop:0.5 #BC9A6B, stop:1 #A67C52);
    border: 2px solid #6F4E37;
}

QPushButton#resetButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #D2B48C, stop:0.5 #C4A484, stop:1 #BC9A6B);
    border: 2px solid #6F4E37;
}

QSlider::groove:horizontal {
    border: 1px solid #999999;
    height: 8px;
    background: #CD853F;
    margin: 2px 0;
    border-radius: 4px;
}

QSlider::handle:horizontal {
    background: #6F4E37;
    border: 2px solid #2F1E15;
    width: 20px;
    margin: -6px 0;
    border-radius: 10px;
}

QSlider::handle:horizontal:hover {
    background: #8B4513;
}

QToolTip {
    background-color: #FFFFE0;
    color: black;
    border: 1px solid #2F1E15;
    padding: 5px;
    border-radius: 3px;
}
"""


class CoffeeVisualizer(QWidget):
    """Widget wizualizacji kubka kawy z zaawansowaną grafiką"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(400, 550)
        self.quality_value = 0
        self.temperature_value = 60
        self.fill_level = 0  # Dla animacji
        
        # Animacja wypełniania
        self.animation = QPropertyAnimation(self, b"fillLevel")
        self.animation.setDuration(800)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        self.animation.setStartValue(0.0)
        self.animation.setEndValue(0.0)
    
    @pyqtProperty(float)
    def fillLevel(self):
        return self.fill_level
    
    @fillLevel.setter
    def fillLevel(self, value):
        self.fill_level = value
        self.update()
    
    def set_coffee(self, quality, temperature):
        """Ustawienie parametrów kawy z animacją"""
        self.quality_value = quality
        self.temperature_value = temperature
        
        # Animacja wypełniania
        target_fill = quality / 100.0
        self.animation.stop()
        self.animation.setStartValue(float(self.fill_level))
        self.animation.setEndValue(float(target_fill))
        self.animation.start()
    
    def clear(self):
        """Natychmiastowe wyczyszczenie kubka bez animacji"""
        self.animation.stop()
        self.quality_value = 0
        self.temperature_value = 60
        self.fill_level = 0
        self.update()
    
    def paintEvent(self, event):
        """Rysowanie kubka z użyciem QPainter"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        
        # Tło
        painter.fillRect(self.rect(), QColor(COLORS['panel_right']))
        
        # Parametry kubka
        center_x = self.width() // 2
        cup_bottom_y = 400
        cup_top_y = 180
        cup_height = cup_bottom_y - cup_top_y
        cup_bottom_width = 140
        cup_top_width = 160
        spodek_y = 420
        
        # Pozycje kubka
        left_bottom = center_x - cup_bottom_width // 2
        right_bottom = center_x + cup_bottom_width // 2
        left_top = center_x - cup_top_width // 2
        right_top = center_x + cup_top_width // 2
        
        # Rysowanie cienia pod spodkiem
        shadow_gradient = QRadialGradient(center_x, spodek_y + 16, 95)
        shadow_gradient.setColorAt(0, QColor(0, 0, 0, 60))
        shadow_gradient.setColorAt(1, QColor(0, 0, 0, 0))
        painter.setBrush(QBrush(shadow_gradient))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(QPointF(center_x, spodek_y + 16), 95, 12)
        
        # Rysowanie spodka
        painter.setPen(QPen(QColor(COLORS['text_dark']), 2))
        saucer_gradient = QLinearGradient(0, spodek_y, 0, spodek_y + 20)
        saucer_gradient.setColorAt(0, QColor(COLORS['accent']).lighter(110))
        saucer_gradient.setColorAt(1, QColor(COLORS['accent']).darker(110))
        painter.setBrush(QBrush(saucer_gradient))
        painter.drawEllipse(QPointF(center_x, spodek_y + 10), 95, 10)
        
        # Rysowanie korpusu kubka z gradientem
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
        
        # Odbicie światła na kubku
        highlight_gradient = QLinearGradient(left_top + 10, cup_top_y, left_top + 30, cup_top_y)
        highlight_gradient.setColorAt(0, QColor(255, 255, 255, 80))
        highlight_gradient.setColorAt(1, QColor(255, 255, 255, 0))
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(highlight_gradient))
        highlight_rect = QRectF(left_top + 5, cup_top_y + 10, 25, cup_height - 20)
        painter.drawRect(highlight_rect)
        
        # Rysowanie uchwytu
        handle_path = QPainterPath()
        handle_x = right_top + 10
        handle_y_top = cup_top_y + 30
        handle_y_bottom = cup_top_y + 120
        
        handle_path.moveTo(handle_x, handle_y_top)
        handle_path.cubicTo(
            handle_x + 50, handle_y_top,
            handle_x + 50, handle_y_bottom,
            handle_x, handle_y_bottom
        )
        
        painter.setPen(QPen(QColor(COLORS['text_dark']), 3))
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(handle_path)
        
        # Rysowanie kawy z animacją
        if self.fill_level > 0:
            coffee_color = self._get_coffee_color(self.quality_value)
            coffee_level = cup_bottom_y - (cup_height * self.fill_level * 0.85)
            
            # Obliczenie szerokości na poziomie kawy
            coffee_width_ratio = (coffee_level - cup_top_y) / cup_height
            coffee_left = left_top + (left_bottom - left_top) * coffee_width_ratio
            coffee_right = right_top + (right_bottom - right_top) * coffee_width_ratio
            
            # Ścieżka wypełnienia kawą z gradientem
            coffee_path = QPainterPath()
            coffee_path.moveTo(coffee_left, coffee_level)
            coffee_path.lineTo(coffee_right, coffee_level)
            coffee_path.lineTo(right_bottom, cup_bottom_y)
            coffee_path.lineTo(left_bottom, cup_bottom_y)
            coffee_path.closeSubpath()
            
            coffee_gradient = QLinearGradient(coffee_left, coffee_level, coffee_right, coffee_level)
            coffee_gradient.setColorAt(0, QColor(coffee_color).darker(110))
            coffee_gradient.setColorAt(0.5, QColor(coffee_color))
            coffee_gradient.setColorAt(1, QColor(coffee_color).darker(110))
            
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(coffee_gradient))
            painter.drawPath(coffee_path)
            
            # Elipsa na powierzchni kawy (3D)
            surface_gradient = QRadialGradient(center_x, coffee_level, (coffee_right - coffee_left) / 2)
            surface_gradient.setColorAt(0, QColor(coffee_color).lighter(110))
            surface_gradient.setColorAt(1, QColor(coffee_color).darker(120))
            
            painter.setBrush(QBrush(surface_gradient))
            painter.drawEllipse(QPointF(center_x, coffee_level), 
                              (coffee_right - coffee_left) / 2, 8)
            
            # Lśniący punkt (odbicie światła)
            highlight = QRadialGradient(center_x - 20, coffee_level - 5, 15)
            highlight.setColorAt(0, QColor(255, 255, 255, 180))
            highlight.setColorAt(1, QColor(255, 255, 255, 0))
            painter.setBrush(QBrush(highlight))
            painter.drawEllipse(QPointF(center_x - 20, coffee_level - 5), 15, 8)
        
        # Rysowanie pary (jeśli temperatura > 75°C)
        if self.temperature_value > 75:
            self._draw_steam(painter, center_x, cup_top_y - 10)
        
        # Tekst pod kubkiem
        painter.setPen(QPen(QColor(COLORS['text_dark']), 1))
        
        # Wartość numeryczna
        font = QFont("Segoe UI", 20, QFont.Bold)
        painter.setFont(font)
        painter.drawText(QRectF(0, 460, self.width(), 30), 
                        Qt.AlignCenter, 
                        f"{self.quality_value:.1f}/100")
        
        # Etykieta słowna
        quality_label = self._get_quality_label(self.quality_value)
        label_color = self._get_label_color(self.quality_value)
        painter.setPen(QPen(QColor(label_color), 1))
        font.setPointSize(14)
        painter.setFont(font)
        painter.drawText(QRectF(0, 490, self.width(), 30), 
                        Qt.AlignCenter, 
                        quality_label)
    
    def _draw_steam(self, painter, center_x, start_y):
        """Rysowanie pary nad kubkiem"""
        painter.setPen(QPen(QColor(211, 211, 211, 150), 3, Qt.SolidLine, Qt.RoundCap))
        
        for i in range(3):
            x_offset = -20 + i * 20
            y_start = start_y - i * 5
            
            steam_path = QPainterPath()
            steam_path.moveTo(center_x + x_offset, y_start)
            
            for t in np.linspace(0, 1, 20):
                x = center_x + x_offset + np.sin(t * 3.14 * 3 + i) * 10
                y = y_start - t * 40
                steam_path.lineTo(x, y)
            
            painter.drawPath(steam_path)
    
    def _get_coffee_color(self, quality_value):
        """Określenie koloru kawy na podstawie jakości"""
        if quality_value < 30:
            return "#C4A484"
        elif quality_value < 50:
            return "#8B6F47"
        elif quality_value < 70:
            return "#6F4E37"
        elif quality_value < 85:
            return "#4A3728"
        else:
            return COLORS['text_dark']
    
    def _get_quality_label(self, quality_value):
        """Określenie etykiety jakości"""
        if quality_value < 30:
            return "Bardzo słaba"
        elif quality_value < 50:
            return "Słaba"
        elif quality_value < 70:
            return "Średnia"
        elif quality_value < 85:
            return "Dobra"
        elif quality_value < 92:
            return "Bardzo dobra"
        else:
            return "Wybitna!"
    
    def _get_label_color(self, quality_value):
        """Określenie koloru etykiety"""
        if quality_value < 30:
            return "#C41E3A"
        elif quality_value < 50:
            return "#FF6347"
        elif quality_value < 70:
            return "#FFD700"
        elif quality_value < 85:
            return "#90EE90"
        else:
            return "#228B22"


class MplCanvas(FigureCanvasQTAgg):
    """Canvas matplotlib dla PyQt5"""
    
    def __init__(self, parent=None, width=9, height=11, dpi=90):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        super().__init__(self.fig)
        self.setParent(parent)
        
        # Subploty
        self.axes = [self.fig.add_subplot(5, 1, i+1) for i in range(5)]
        self.fig.tight_layout(pad=2.5)


class ProgressBarWidget(QWidget):
    """Widget paska postępu z animacją"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(50)
        self.progress_value = 0
        
        # Animacja
        self.animation = QPropertyAnimation(self, b"progressValue")
        self.animation.setDuration(800)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        self.animation.setStartValue(0.0)
        self.animation.setEndValue(0.0)
    
    @pyqtProperty(float)
    def progressValue(self):
        return self.progress_value
    
    @progressValue.setter
    def progressValue(self, value):
        self.progress_value = value
        self.update()
    
    def set_progress(self, value):
        """Ustawienie wartości postępu z animacją"""
        self.animation.stop()
        self.animation.setStartValue(float(self.progress_value))
        self.animation.setEndValue(float(value))
        self.animation.start()
    
    def reset(self):
        """Natychmiastowy reset bez animacji"""
        self.animation.stop()
        self.progress_value = 0
        self.update()
    
    def paintEvent(self, event):
        """Rysowanie paska postępu"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Tło
        painter.fillRect(self.rect(), QColor("#CCCCCC"))
        painter.setPen(QPen(QColor(COLORS['text_dark']), 2))
        painter.drawRect(self.rect())
        
        # Wypełnienie z gradientem
        fill_width = int((self.progress_value / 100.0) * self.width())
        
        if fill_width > 0:
            gradient = QLinearGradient(0, 0, fill_width, 0)
            color = self._get_color(self.progress_value)
            gradient.setColorAt(0, QColor(color).darker(110))
            gradient.setColorAt(0.5, QColor(color))
            gradient.setColorAt(1, QColor(color).lighter(110))
            
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(gradient))
            painter.drawRect(0, 0, fill_width, self.height())
        
        # Ikona filiżanki
        if fill_width > 0:
            painter.setPen(QPen(Qt.black))
            font = QFont("Arial", 24)
            painter.setFont(font)
            painter.drawText(QRectF(fill_width + 10, 0, 40, self.height()),
                           Qt.AlignVCenter | Qt.AlignLeft, "☕")
    
    def _get_color(self, value):
        """Określenie koloru na podstawie wartości - odcienie brązu"""
        if value < 20:
            return "#D2B48C"  # Tan - bardzo jasny brąz
        elif value < 40:
            return "#BC9A6B"  # Jaśniejszy brąz
        elif value < 60:
            return "#A67C52"  # Średni brąz
        elif value < 75:
            return "#8B6F47"  # Ciemniejszy brąz
        elif value < 85:
            return "#6F4E37"  # Brąz kawowy
        else:
            return "#4A3728"  # Bardzo ciemny brąz - najlepsza kawa


class CoffeeGUI(QMainWindow):
    """Główna klasa GUI aplikacji BrewSense"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BrewSense - System Oceny Jakości Kawy")
        self.setGeometry(0, 0, 1920, 1080)
        
        # Inicjalizacja systemu rozmytego
        self.fuzzy_system = CoffeeQualitySystem()
        self.current_quality = 0
        
        # Stylowanie
        self.setStyleSheet(QSS_STYLE)
        
        # Tworzenie interfejsu
        self._create_widgets()
    
    def _create_widgets(self):
        """Tworzenie wszystkich widgetów"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Główny layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Górna część (3 panele)
        top_splitter = QSplitter(Qt.Horizontal)
        
        # Panel lewy
        left_panel = self._create_left_panel()
        top_splitter.addWidget(left_panel)
        
        # Panel środkowy
        middle_panel = self._create_middle_panel()
        top_splitter.addWidget(middle_panel)
        
        # Panel prawy
        right_panel = self._create_right_panel()
        top_splitter.addWidget(right_panel)
        
        # Proporcje paneli (2:6:3)
        top_splitter.setStretchFactor(0, 2)
        top_splitter.setStretchFactor(1, 6)
        top_splitter.setStretchFactor(2, 3)
        
        main_layout.addWidget(top_splitter, stretch=9)
        
        # Panel dolny
        bottom_panel = self._create_bottom_panel()
        main_layout.addWidget(bottom_panel, stretch=1)
    
    def _create_left_panel(self):
        """Tworzenie lewego panelu z suwakami"""
        panel = QFrame()
        panel.setStyleSheet(f"background-color: {COLORS['panel_left']}; border-radius: 10px;")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(15)
        
        # Tytuł
        title = QLabel("Parametry Kawy")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        layout.addSpacing(20)

        """Tworzenie lewego panelu z suwakami i wyborem profilu"""
        panel = QFrame()
        panel.setStyleSheet(f"background-color: {COLORS['panel_left']}; border-radius: 10px;")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(15)

        # Tytuł
        title = QLabel("Parametry Kawy")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        layout.addSpacing(10)

        # --- SEKACJA PROFILI (DODANO) ---
        profile_label = QLabel("Wybierz profil kawy:")
        profile_label.setFont(QFont("Segoe UI", 11, QFont.Bold))
        layout.addWidget(profile_label)

        self.profile_combo = QComboBox()
        self.profile_combo.addItems(COFFEE_PROFILES.keys())
        self.profile_combo.setStyleSheet("""
                    QComboBox {
                        padding: 8px;
                        border: 1px solid #8B6F47;
                        border-radius: 5px;
                        background-color: #FFF8E7;
                        font-size: 13px;
                    }
                """)
        self.profile_combo.currentTextChanged.connect(self.load_profile)
        layout.addWidget(self.profile_combo)

        self.profile_desc_label = QLabel("Ręczne ustawienia parametrów.")
        self.profile_desc_label.setWordWrap(True)
        self.profile_desc_label.setStyleSheet("font-size: 11px; font-style: italic; color: #4A3728;")
        layout.addWidget(self.profile_desc_label)
        layout.addSpacing(10)

        # Suwaki
        self.bitterness_slider, self.bitterness_label = self._create_slider(
            layout, "Gorzkość (Bitterness):", 0, 100, 50,
            "Intensywność goryczy (0=brak, 10=bardzo gorzka)"
        )
        
        self.acidity_slider, self.acidity_label = self._create_slider(
            layout, "Kwasowość (Acidity):", 0, 100, 50,
            "Poziom kwasowości (0=płaska, 10=bardzo kwaśna)"
        )
        
        self.aroma_slider, self.aroma_label = self._create_slider(
            layout, "Aromat (Aroma):", 0, 100, 50,
            "Bogactwo i intensywność zapachu kawy"
        )
        
        self.temperature_slider, self.temperature_label = self._create_slider(
            layout, "Temperatura (Temperature):", 600, 950, 800,
            "Temperatura podania (60-95°C)", is_temperature=True
        )
        
        layout.addSpacing(30)
        
        # Przyciski
        evaluate_btn = QPushButton("Oceń Kawę")
        evaluate_btn.clicked.connect(self.evaluate_coffee)
        evaluate_btn.setCursor(Qt.PointingHandCursor)  # Kursor wskazujący
        layout.addWidget(evaluate_btn)
        
        reset_btn = QPushButton("Reset")
        reset_btn.setObjectName("resetButton")
        reset_btn.clicked.connect(self.reset_values)
        reset_btn.setCursor(Qt.PointingHandCursor)  # Kursor wskazujący
        layout.addWidget(reset_btn)
        
        layout.addStretch()
        
        return panel
    
    def _create_slider(self, layout, label_text, min_val, max_val, default_val, tooltip, is_temperature=False):
        """Tworzenie suwaka z etykietą"""
        # Ramka dla suwaka
        frame = QFrame()
        frame.setStyleSheet("background-color: transparent; border: 1px solid #999; border-radius: 5px; padding: 10px;")
        frame_layout = QVBoxLayout(frame)
        frame_layout.setContentsMargins(10, 10, 10, 10)
        
        # Etykieta
        label = QLabel(label_text)
        label.setFont(QFont("Segoe UI", 11))
        frame_layout.addWidget(label)
        
        # Kontener dla suwaka i wartości
        slider_container = QHBoxLayout()
        
        # Suwak
        slider = QSlider(Qt.Horizontal)
        slider.setMinimum(min_val)
        slider.setMaximum(max_val)
        slider.setValue(default_val)
        slider.setToolTip(tooltip)
        slider_container.addWidget(slider)
        
        # Etykieta wartości
        if is_temperature:
            value_label = QLabel(f"{default_val/10:.1f}°C")
        else:
            value_label = QLabel(f"{default_val/10:.1f}")
        value_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        value_label.setMinimumWidth(80)
        value_label.setAlignment(Qt.AlignCenter)
        slider_container.addWidget(value_label)
        
        frame_layout.addLayout(slider_container)
        
        # Aktualizacja wartości
        def update_value(val):
            if is_temperature:
                value_label.setText(f"{val/10:.1f}°C")
            else:
                value_label.setText(f"{val/10:.1f}")
        
        slider.valueChanged.connect(update_value)
        
        layout.addWidget(frame)
        
        return slider, value_label

    def load_profile(self, profile_name):
        """Ładuje parametry dla wybranego profilu kawy"""
        data = COFFEE_PROFILES[profile_name]

        # Aktualizacja opisu
        self.profile_desc_label.setText(data["desc"])

        # Jeśli wybrano profil z parametrami (nie "Własny")
        if data["params"]:
            params = data["params"]

            # Ustawiamy wartości bezpośrednio - usunięto blockSignals,
            # dzięki czemu etykiety liczbowe (np. "8.0") zaktualizują się automatycznie
            self.bitterness_slider.setValue(int(params["bitterness"] * 10))
            self.acidity_slider.setValue(int(params["acidity"] * 10))
            self.aroma_slider.setValue(int(params["aroma"] * 10))
            self.temperature_slider.setValue(int(params["temperature"] * 10))

            # Wymuszamy ocenę kawy po załadowaniu profilu, aby zaktualizować wykresy i wynik
            self.evaluate_coffee()
    
    def _create_middle_panel(self):
        """Tworzenie środkowego panelu z wykresami"""
        panel = QFrame()
        panel.setStyleSheet(f"background-color: {COLORS['panel_middle']}; border-radius: 10px;")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Tytuł
        title = QLabel("Wykresy Funkcji Przynależności")
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Canvas matplotlib
        self.plot_canvas = MplCanvas(panel, width=9, height=11, dpi=90)
        layout.addWidget(self.plot_canvas)
        
        self._initialize_plots()
        
        return panel
    
    def _create_right_panel(self):
        """Tworzenie prawego panelu z wizualizacją kubka"""
        panel = QFrame()
        panel.setStyleSheet(f"background-color: {COLORS['panel_right']}; border-radius: 10px;")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(25, 25, 25, 25)
        
        # Tytuł
        title = QLabel("Wizualizacja Jakości")
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        layout.addSpacing(20)
        
        # Wizualizacja kubka
        self.visualizer = CoffeeVisualizer()
        layout.addWidget(self.visualizer)
        
        layout.addStretch()
        
        return panel
    
    def _create_bottom_panel(self):
        """Tworzenie dolnego panelu z wynikiem"""
        panel = QFrame()
        panel.setStyleSheet(f"background-color: {COLORS['panel_bottom']}; border-radius: 10px;")
        panel.setMaximumHeight(120)
        layout = QHBoxLayout(panel)
        layout.setContentsMargins(25, 20, 25, 20)
        
        # Wynik
        self.result_label = QLabel("Wynik: 0.0/100")
        self.result_label.setFont(QFont("Segoe UI", 28, QFont.Bold))
        layout.addWidget(self.result_label)
        
        # Pasek postępu
        self.progress_bar = ProgressBarWidget()
        layout.addWidget(self.progress_bar, stretch=1)
        
        # Opis
        self.description_label = QLabel("")
        self.description_label.setFont(QFont("Segoe UI", 20, QFont.Bold))
        self.description_label.setMinimumWidth(200)
        self.description_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.description_label)

        report_btn = QPushButton("📋 Raport")
        report_btn.setToolTip("Pokaż szczegółowe wyjaśnienie wyniku")
        report_btn.setCursor(Qt.PointingHandCursor)
        report_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #FFF8E7; 
                        border: 2px solid #6F4E37;
                        padding: 10px 15px;
                    }
                    QPushButton:hover { background-color: #FFFFFF; }
                """)
        report_btn.clicked.connect(self.show_explanation_dialog)
        layout.addWidget(report_btn)

        return panel
    
    def _initialize_plots(self):
        """Inicjalizacja pustych wykresów"""
        for ax in self.plot_canvas.axes:
            ax.clear()
            ax.grid(True, alpha=0.3)
        
        self.plot_canvas.fig.tight_layout(pad=2.5)
        self.plot_canvas.draw()
    
    def _update_plots(self):
        """Aktualizacja wykresów"""
        variables = self.fuzzy_system.get_variables()
        
        input_vars = ['bitterness', 'acidity', 'aroma', 'temperature']
        titles = ['Gorzkość (Bitterness)', 'Kwasowość (Acidity)', 
                 'Aromat (Aroma)', 'Temperatura (Temperature)', 
                 'Jakość (Quality) - Defuzzyfikacja']
        units = ['Wartość', 'Wartość', 'Wartość', '°C', 'Wartość (0-100)']
        input_values = [
            self.bitterness_slider.value() / 10,
            self.acidity_slider.value() / 10,
            self.aroma_slider.value() / 10,
            self.temperature_slider.value() / 10
        ]
        
        for i, ax in enumerate(self.plot_canvas.axes):
            ax.clear()
            
            var_name = input_vars[i] if i < 4 else 'quality'
            var = variables[var_name]
            
            for label in var.terms:
                ax.plot(var.universe, var[label].mf, label=label, linewidth=1.5)
            
            if i < 4:
                ax.axvline(input_values[i], color=COLORS['text_dark'], 
                          linestyle='--', linewidth=2)
            else:
                ax.axvline(self.current_quality, color=COLORS['button_primary'], 
                          linestyle='--', linewidth=2, label='Wynik')
            
            ax.set_title(titles[i], fontsize=10)
            ax.set_xlabel(units[i], fontsize=8)
            ax.set_ylabel('Przynależność', fontsize=8)
            ax.legend(fontsize=7, loc='upper right')
            ax.grid(True, alpha=0.3)
        
        self.plot_canvas.fig.tight_layout(pad=2.5)
        self.plot_canvas.draw()
    
    def evaluate_coffee(self):
        """Ocena kawy"""
        # Pobranie wartości
        bitterness = self.bitterness_slider.value() / 10
        acidity = self.acidity_slider.value() / 10
        aroma = self.aroma_slider.value() / 10
        temperature = self.temperature_slider.value() / 10
        
        # Obliczenie jakości
        quality = self.fuzzy_system.evaluate(bitterness, acidity, aroma, temperature)
        self.current_quality = quality
        
        # Aktualizacja wizualizacji
        self.visualizer.set_coffee(quality, temperature)
        
        # Aktualizacja wykresów
        self._update_plots()
        
        # Aktualizacja wyniku
        self.result_label.setText(f"Wynik: {quality:.1f}/100")
        self.progress_bar.set_progress(quality)
        
        # Aktualizacja opisu
        quality_label = self.visualizer._get_quality_label(quality)
        label_color = self.visualizer._get_label_color(quality)
        self.description_label.setText(quality_label)
        self.description_label.setStyleSheet(f"color: {label_color};")
    
    def reset_values(self):
        """Reset wartości"""
        self.profile_combo.setCurrentIndex(0)  # Ustawia "Własny"

        self.bitterness_slider.setValue(50)
        self.acidity_slider.setValue(50)
        self.aroma_slider.setValue(50)
        self.temperature_slider.setValue(800)
        
        self.current_quality = 0
        
        # Użycie nowych metod bez animacji dla resetu
        self.visualizer.clear()
        self.progress_bar.reset()
        
        self._initialize_plots()
        
        self.result_label.setText("Wynik: 0.0/100")
        self.description_label.setText("")

    def show_explanation_dialog(self):
        """Wyświetla okno dialogowe ze szczegółowym wyjaśnieniem wyniku"""
        # Pobranie aktualnych wartości
        bitterness = self.bitterness_slider.value() / 10
        acidity = self.acidity_slider.value() / 10
        aroma = self.aroma_slider.value() / 10
        temperature = self.temperature_slider.value() / 10

        # Pobranie tekstu wyjaśnienia z systemu rozmytego
        explanation = self.fuzzy_system.explain_result(
            bitterness, acidity, aroma, temperature, self.current_quality
        )

        # Dodanie informacji o wybranym profilu
        current_profile = self.profile_combo.currentText()
        profile_info = f"PROFIL: {current_profile}\n{COFFEE_PROFILES[current_profile]['desc']}\n\n"

        full_text = profile_info + explanation

        # Wyświetlenie MessageBox
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Raport Jakości Kawy - BrewSense")
        msg_box.setText(full_text)
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setStyleSheet(f"background-color: {COLORS['background']}; color: {COLORS['text_dark']};")
        msg_box.exec_()


def main():
    """Funkcja główna"""
    app = QApplication(sys.argv)
    window = CoffeeGUI()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()