"""
Interfejs graficzny dla systemu BrewSense
Implementacja GUI z wizualizacją kubka kawy i wykresami
"""

import tkinter as tk
from tkinter import ttk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
# Zakładam, że plik fuzzy_system.py istnieje
try:
    from fuzzy_system import CoffeeQualitySystem
except ImportError:
    class CoffeeQualitySystem:
        """Dummy class for testing if fuzzy_system is missing"""
        def evaluate(self, b, a, ar, t): return 75.0
        def get_variables(self): return {'bitterness': object(), 'acidity': object(), 'aroma': object(), 'temperature': object(), 'quality': object()}
        def get_quality_label(self, q): return "Bardzo dobra"


# Nowa paleta kolorów (ciepła, kawowa)
COLORS = {
    'background': '#F5F5DC',  # Beżowy (beige)
    'panel_left': '#E8DCC4',  # Jasny brąz
    'panel_middle': '#FFFFFF',  # Biały
    'panel_right': '#FFF8E7',  # Kremowy
    'panel_bottom': '#D2B48C',  # Tan
    'button_primary': '#6F4E37',  # Brąz kawowy
    'button_secondary': '#8B4513', # Sienna
    'text_dark': '#2F1E15',  # Ciemny brąz
    'accent': '#CD853F',  # Peru (akcent)
}

# Propozycja ujednolicenia czcionek
FONTS = {
    'title': ('Segoe UI', 16, 'bold'),
    'heading': ('Segoe UI', 14, 'bold'),
    'label': ('Segoe UI', 11),
    'value': ('Segoe UI', 12, 'bold'), # Zwiększone
    'button': ('Segoe UI', 13, 'bold'),
    'result_big': ('Segoe UI', 28, 'bold'),
    'result_desc': ('Segoe UI', 20, 'bold'),
}

# Funkcja pomocnicza do tworzenia Tooltip (poza klasą)
class Tooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None
        self.widget.bind('<Enter>', self.show_tooltip)
        self.widget.bind('<Leave>', self.hide_tooltip)

    def show_tooltip(self, event):
        if self.tip_window or not self.text:
            return
        x, y, cx, cy = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20
        
        self.tip_window = tk.Toplevel(self.widget)
        self.tip_window.wm_overrideredirect(True)
        self.tip_window.wm_geometry(f"+{x}+{y}")
        
        label = tk.Label(self.tip_window, text=self.text, justify=tk.LEFT,
                         background="#FFFFE0", relief='solid', borderwidth=1,
                         font=('Arial', 9))
        label.pack(ipadx=1)

    def hide_tooltip(self, event):
        if self.tip_window:
            self.tip_window.destroy()
        self.tip_window = None


class CoffeeVisualizer:
    """Klasa odpowiedzialna za rysowanie wizualizacji kubka kawy"""
    
    def __init__(self, canvas):
        """
        Inicjalizacja wizualizera
        
        Args:
            canvas: Widget Canvas z tkinter
        """
        self.canvas = canvas
        # Zwiększenie rozmiaru canvas (Zadanie 1)
        self.canvas_width = 400
        self.canvas_height = 550
        self.canvas.config(width=self.canvas_width, height=self.canvas_height)
    
    def _hex_to_rgb(self, hex_color):
        """Konwertuje kolor HEX na krotkę RGB"""
        h = hex_color.lstrip('#')
        return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
        
    def draw_cup(self, quality_value, temperature_val):
        """
        Rysowanie kubka z kawą - NAPRAWIONY PROBLEM Z UCIĘCIEM
        
        Args:
            quality_value (float): Jakość kawy (0-100)
            temperature_val (float): Temperatura kawy (60-95°C)
        """
        # Czyszczenie canvas
        self.canvas.delete("all")
        
        # Parametry kubka (dostosowane do canvas_height = 550)
        center_x = self.canvas_width // 2
        
        # Pozycje zgodne z wymaganiami
        cup_bottom_y = 400  # Było 320
        cup_top_y = 180     # Było 150
        spodek_y = 420      # Nowa pozycja spodka
        
        cup_height = cup_bottom_y - cup_top_y
        cup_bottom_width = 140 # Zwiększone
        cup_top_width = 160    # Zwiększone
        
        # Obliczenie pozycji kubka
        left_bottom = center_x - cup_bottom_width // 2
        right_bottom = center_x + cup_bottom_width // 2
        left_top = center_x - cup_top_width // 2
        right_top = center_x + cup_top_width // 2
        
        # Rysowanie cienia pod spodkiem
        self.canvas.create_oval(
            center_x - 90, spodek_y + 8,
            center_x + 95, spodek_y + 25,
            fill="#000000", outline="", stipple="gray25"
        )
        
        # Rysowanie spodka
        self.canvas.create_oval(
            center_x - 95, spodek_y,
            center_x + 95, spodek_y + 20,
            fill=COLORS['accent'], outline=COLORS['text_dark'], width=2
        )
        
        # Rysowanie korpusu kubka (trapez)
        cup_points = [
            left_top, cup_top_y,
            right_top, cup_top_y,
            right_bottom, cup_bottom_y,
            left_bottom, cup_bottom_y
        ]
        self.canvas.create_polygon(
            cup_points,
            fill=COLORS['panel_right'], outline=COLORS['text_dark'], width=3
        )

        # Gradient/Odbicie światła 3D na kubku
        self.canvas.create_line(
            left_top + 5, cup_top_y + 5,
            left_bottom + 5, cup_bottom_y - 5,
            fill="#FFFFFF", width=3, stipple="gray50" 
        )
        
        # Rysowanie uchwytu
        handle_x = right_top + 10
        handle_y_top = cup_top_y + 30
        handle_y_bottom = cup_top_y + 120 # Trochę niższy uchwyt
        
        self.canvas.create_arc(
            handle_x, handle_y_top,
            handle_x + 40, handle_y_bottom,
            start=270, extent=180, style=tk.ARC,
            outline=COLORS['text_dark'], width=3
        )
        
        # Określenie koloru kawy na podstawie jakości
        coffee_color = self._get_coffee_color(quality_value)
        
        # Obliczenie poziomu wypełnienia (proporcjonalnie do jakości)
        fill_percentage = quality_value / 100.0
        coffee_level = cup_bottom_y - (cup_height * fill_percentage * 0.85)
        
        # Rysowanie kawy (wypełnienie)
        if fill_percentage > 0:
            # Obliczenie szerokości na poziomie kawy (interpolacja liniowa)
            coffee_width_ratio = (coffee_level - cup_top_y) / cup_height
            coffee_left = left_top + (left_bottom - left_top) * coffee_width_ratio
            coffee_right = right_top + (right_bottom - right_top) * coffee_width_ratio
            
            coffee_points = [
                coffee_left, coffee_level,
                coffee_right, coffee_level,
                right_bottom, cup_bottom_y,
                left_bottom, cup_bottom_y
            ]
            
            self.canvas.create_polygon(
                coffee_points,
                fill=coffee_color, outline=""
            )
            
            # Rysowanie elipsy na powierzchni kawy (efekt 3D)
            self.canvas.create_oval(
                coffee_left, coffee_level - 5,
                coffee_right, coffee_level + 5,
                fill=self._darken_color(coffee_color), outline=""
            )
            
            # Lśniący punkt na kawie (Odbicie światła)
            self.canvas.create_oval(
                center_x - 20, coffee_level - 8,
                center_x, coffee_level - 5,
                fill="#FFFFFF", outline="", tags="highlight"
            )
        
        # Rysowanie pary (jeśli temperatura > 75°C)
        if temperature_val > 75:
            self._draw_steam(center_x, cup_top_y - 10)
        
        # Rysowanie wyniku pod kubkiem (nowe pozycje, aby nie były ucięte)
        quality_label = self._get_quality_label(quality_value)
        
        # Wartość numeryczna
        self.canvas.create_text(
            center_x, 460, # Nowa pozycja y
            text=f"{quality_value:.1f}/100",
            font=FONTS['result_desc'],
            fill=COLORS['text_dark']
        )
        
        # Etykieta słowna
        label_color = self._get_label_color(quality_value)
        self.canvas.create_text(
            center_x, 490, # Nowa pozycja y
            text=quality_label,
            font=FONTS['heading'],
            fill=label_color
        )
    
    def _draw_steam(self, center_x, start_y):
        """Rysowanie pary nad kubkiem (ulepszone, bardziej faliste)"""
        steam_color = "#D3D3D3"
        
        # Trzy fale pary
        for i in range(3):
            x_offset = -20 + i * 20
            y_start = start_y - i * 5
            
            # Fala jako krzywa
            points = []
            for t in np.linspace(0, 1, 30):
                x = center_x + x_offset + np.sin(t * 3.14 * 3 + i) * 10
                y = y_start - t * 40
                points.extend([x, y])
            
            self.canvas.create_line(
                points,
                smooth=True, width=3, fill=steam_color, stipple="gray50" # Półprzezroczysta
            )
    
    def _get_coffee_color(self, quality_value):
        """Określenie koloru kawy na podstawie jakości"""
        if quality_value < 30:
            return "#C4A484"  # Jasnobrązowy
        elif quality_value < 50:
            return "#8B6F47"  # Średni brąz
        elif quality_value < 70:
            return "#6F4E37"  # Ciemny brąz
        elif quality_value < 85:
            return "#4A3728"  # Bardzo ciemny
        else:
            return COLORS['text_dark'] # Prawie czarny
    
    def _darken_color(self, color):
        """Przyciemnienie koloru (dla efektu 3D)"""
        # Używamy helpera _hex_to_rgb
        try:
            rgb = self._hex_to_rgb(color)
        except ValueError:
            rgb = (100, 100, 100) # Fallback
            
        darker_rgb = tuple(min(255, int(c * 0.7)) for c in rgb)
        return f"#{darker_rgb[0]:02x}{darker_rgb[1]:02x}{darker_rgb[2]:02x}"
    
    def _get_quality_label(self, quality_value):
        """Określenie etykiety jakości (przeniesione z CoffeeGUI)"""
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
        """Określenie koloru etykiety na podstawie jakości"""
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
    
    def clear_cup(self):
        """Wyczyszczenie kubka (pusty kubek)"""
        self.canvas.delete("all")
        self.draw_cup(0, 60)


class CoffeeGUI:
    """Główna klasa interfejsu graficznego aplikacji BrewSense"""
    
    def __init__(self):
        """Inicjalizacja GUI"""
        self.root = tk.Tk()
        self.root.title("BrewSense - System Oceny Jakości Kawy")
        # Rozmiar 1920x1080 (Full HD)
        self.root.geometry("1920x1080")
        self.root.resizable(True, True) 
        
        # Inicjalizacja systemu rozmytego
        self.fuzzy_system = CoffeeQualitySystem()
        
        # Wartości domyślne
        self.current_quality = 0
        
        # Tworzenie interfejsu
        self._create_widgets()
        
    def _create_widgets(self):
        """Tworzenie wszystkich widgetów GUI"""
        
        # Główny frame z nowym tłem
        main_frame = tk.Frame(self.root, bg=COLORS['background'])
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Konfiguracja siatki (Lepsze proporcje)
        main_frame.grid_rowconfigure(0, weight=9) 
        main_frame.grid_rowconfigure(1, weight=1)  

        main_frame.grid_columnconfigure(0, weight=2)  # Panel lewy (parametry)
        main_frame.grid_columnconfigure(1, weight=6)  # Panel środkowy (wykresy)
        main_frame.grid_columnconfigure(2, weight=3)  # Panel prawy (kubek)
        
        # Panel lewy (parametry)
        self._create_left_panel(main_frame)
        
        # Panel środkowy (wykresy)
        self._create_middle_panel(main_frame)
        
        # Panel prawy (kubek)
        self._create_right_panel(main_frame)
        
        # Panel dolny (wynik)
        self._create_bottom_panel(main_frame)
    
    def _create_left_panel(self, parent):
        """Tworzenie lewego panelu z suwakami"""
        # Ramka lewego panelu z efektem 3D dla estetyki
        left_frame = tk.Frame(
            parent, bg=COLORS['panel_left'], padx=25, pady=25,
            bd=3, relief=tk.RIDGE, # Dodanie obramowania
            highlightbackground=COLORS['text_dark'], highlightcolor=COLORS['text_dark'], highlightthickness=1
        )
        left_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # Tytuł
        title = tk.Label(
            left_frame, text="Parametry Kawy",
            font=FONTS['title'], bg=COLORS['panel_left'], fg=COLORS['text_dark']
        )
        title.pack(pady=(0, 20))
        
        # Suwaki
        self.bitterness_var = tk.DoubleVar(value=5.0)
        self.acidity_var = tk.DoubleVar(value=5.0)
        self.aroma_var = tk.DoubleVar(value=5.0)
        self.temperature_var = tk.DoubleVar(value=80.0)
        
        # Gorzkość
        self._create_slider(
            left_frame, "Gorzkość (Bitterness):",
            self.bitterness_var, 0, 10, "", "Intensywność goryczy (0=brak, 10=bardzo gorzka)"
        )
        
        # Kwasowość
        self._create_slider(
            left_frame, "Kwasowość (Acidity):",
            self.acidity_var, 0, 10, "", "Poziom kwasowości (0=płaska, 10=bardzo kwaśna)"
        )
        
        # Aromat
        self._create_slider(
            left_frame, "Aromat (Aroma):",
            self.aroma_var, 0, 10, "", "Bogactwo i intensywność zapachu kawy"
        )
        
        # Temperatura
        self._create_slider(
            left_frame, "Temperatura (Temperature):",
            self.temperature_var, 60, 95, "°C", "Temperatura podania (60-95°C)"
        )
        
        # Przyciski
        button_frame = tk.Frame(left_frame, bg=COLORS['panel_left'])
        button_frame.pack(pady=30)
        
        # Przycisk "Oceń Kawę"
        evaluate_btn = tk.Button(
            button_frame, text="Oceń Kawę",
            font=FONTS['button'],
            bg=COLORS['button_primary'], fg="white",
            padx=30, pady=10,
            command=self.evaluate_coffee,
            bd=2, relief=tk.RAISED
        )
        evaluate_btn.pack(pady=5)
        
        # Przycisk "Reset"
        reset_btn = tk.Button(
            button_frame, text="Reset",
            font=("Segoe UI", 12),
            bg=COLORS['button_secondary'], fg="white",
            padx=30, pady=8,
            command=self.reset_values,
            bd=2, relief=tk.RAISED
        )
        reset_btn.pack(pady=5)
    
    def _create_slider(self, parent, label_text, variable, from_, to, unit, tooltip_text=""):
        """
        Tworzenie suwaka z etykietą, ulepszone o obramowanie
        """
        # Ramka dla każdego suwaka z lekkim obramowaniem (GROOVE)
        frame = tk.Frame(
            parent, bg=COLORS['panel_left'],
            bd=1, relief=tk.GROOVE, # Subtelne obramowanie
            padx=5, pady=5
        )
        frame.pack(fill=tk.X, pady=10)
        
        # Etykieta
        label = tk.Label(
            frame, text=label_text,
            font=FONTS['label'], bg=COLORS['panel_left'], fg=COLORS['text_dark']
        )
        label.pack(anchor="w")
        
        # Frame dla suwaka i wartości
        slider_frame = tk.Frame(frame, bg=COLORS['panel_left'])
        slider_frame.pack(fill=tk.X, pady=5)
        
        # Suwak (długość 250, z jednolitym stylem obramowania)
        slider = tk.Scale(
            slider_frame, from_=from_, to=to,
            orient=tk.HORIZONTAL, variable=variable,
            resolution=0.1, length=250, 
            bg=COLORS['panel_left'], troughcolor=COLORS['accent'],
            # Dodatkowe ustawienia dla "obramowania" i wyglądu
            highlightthickness=1, 
            highlightbackground=COLORS['text_dark'],
            highlightcolor=COLORS['text_dark'],
            bd=0 
        )
        slider.pack(side=tk.LEFT)
        
        # Tooltip
        if tooltip_text:
            Tooltip(slider, tooltip_text)

        # Etykieta z wartością (większy font)
        value_label = tk.Label(
            slider_frame, text=f"{variable.get():.1f}{unit}",
            font=FONTS['value'], bg=COLORS['panel_left'], fg=COLORS['text_dark'], width=8
        )
        value_label.pack(side=tk.LEFT, padx=10)
        
        # Aktualizacja wartości przy zmianie
        def update_value(*args):
            value_label.config(text=f"{variable.get():.1f}{unit}")
        
        variable.trace('w', update_value)
    
    def _create_middle_panel(self, parent):
        """Tworzenie środkowego panelu z wykresami"""
        # Ramka środkowego panelu z efektem 3D
        middle_frame = tk.Frame(
            parent, bg=COLORS['panel_middle'], padx=15, pady=15,
            bd=3, relief=tk.RIDGE
        )
        middle_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        
        # Tytuł
        title = tk.Label(
            middle_frame, text="Wykresy Funkcji Przynależności",
            font=FONTS['heading'], bg=COLORS['panel_middle'], fg=COLORS['text_dark']
        )
        title.pack(pady=(0, 10))
        
        # Figure dla wykresów 
        self.fig = Figure(figsize=(9, 11), dpi=90) 
        self.canvas_plot = FigureCanvasTkAgg(self.fig, master=middle_frame)
        self.canvas_plot.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Początkowe puste wykresy
        self._initialize_plots()
    
    def _create_right_panel(self, parent):
        """Tworzenie prawego panelu z wizualizacją kubka"""
        # Ramka prawego panelu z efektem 3D
        right_frame = tk.Frame(
            parent, bg=COLORS['panel_right'], padx=25, pady=25,
            bd=3, relief=tk.RIDGE
        )
        right_frame.grid(row=0, column=2, sticky="nsew", padx=10, pady=10)
        
        # Tytuł
        title = tk.Label(
            right_frame, text="Wizualizacja Jakości",
            font=FONTS['heading'], bg=COLORS['panel_right'], fg=COLORS['text_dark']
        )
        title.pack(pady=(0, 20))
        
        # Canvas dla kubka 
        self.cup_canvas = tk.Canvas(
            right_frame, width=400, height=550, 
            bg=COLORS['panel_right'], highlightthickness=0
        )
        self.cup_canvas.pack(fill=tk.BOTH, expand=True) 
        
        # Inicjalizacja wizualizera
        self.visualizer = CoffeeVisualizer(self.cup_canvas)
        self.visualizer.draw_cup(0, 60)
    
    def _create_bottom_panel(self, parent):
        """Tworzenie dolnego panelu z wynikiem"""
        # Ramka dolnego panelu z efektem 3D
        bottom_frame = tk.Frame(
            parent, bg=COLORS['panel_bottom'], padx=25, pady=20,
            bd=3, relief=tk.GROOVE
        )
        bottom_frame.grid(row=1, column=0, columnspan=3, sticky="ew", padx=10, pady=10)
        
        # Etykieta wyniku (większy font)
        self.result_label = tk.Label(
            bottom_frame, text="Wynik: 0.0/100",
            font=FONTS['result_big'], bg=COLORS['panel_bottom'], fg=COLORS['text_dark']
        )
        self.result_label.pack(side=tk.LEFT, padx=20)
        
        # Pasek postępu
        self.progress_frame = tk.Frame(bottom_frame, bg=COLORS['panel_bottom'])
        self.progress_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=20)
        
        self.progress_canvas = tk.Canvas(
            self.progress_frame, height=50, bg=COLORS['panel_bottom'],
            highlightthickness=0
        )
        self.progress_canvas.pack(fill=tk.X)
        
        # Etykieta opisu
        self.description_label = tk.Label(
            bottom_frame, text="",
            font=FONTS['result_desc'], bg=COLORS['panel_bottom'], fg=COLORS['text_dark']
        )
        self.description_label.pack(side=tk.LEFT, padx=20)
        
        # Początkowy pasek postępu
        self._update_progress_bar(0)
    
    def _initialize_plots(self):
        """Inicjalizacja pustych wykresów"""
        self.fig.clear()
        
        # 5 subplotów (4 dla wejść, 1 dla wyjścia)
        self.ax1 = self.fig.add_subplot(5, 1, 1)
        self.ax2 = self.fig.add_subplot(5, 1, 2)
        self.ax3 = self.fig.add_subplot(5, 1, 3)
        self.ax4 = self.fig.add_subplot(5, 1, 4)
        self.ax5 = self.fig.add_subplot(5, 1, 5)
        
        # Lepsze odstępy (pad=2.5)
        self.fig.tight_layout(pad=2.5)
        self.canvas_plot.draw()
    
    def _update_plots(self):
        """Aktualizacja wykresów po obliczeniu"""
        self.fig.clear()
        
        variables = self.fuzzy_system.get_variables()
        
        # Lista osi
        axes = [self.fig.add_subplot(5, 1, i+1) for i in range(5)]
        input_vars = ['bitterness', 'acidity', 'aroma', 'temperature']
        titles = ['Gorzkość (Bitterness)', 'Kwasowość (Acidity)', 'Aromat (Aroma)', 'Temperatura (Temperature)', 'Jakość (Quality) - Defuzzyfikacja']
        units = ['Wartość', 'Wartość', 'Wartość', '°C', 'Wartość (0-100)']
        input_values = [self.bitterness_var.get(), self.acidity_var.get(), self.aroma_var.get(), self.temperature_var.get()]
        
        for i, ax in enumerate(axes):
            var_name = input_vars[i] if i < 4 else 'quality'
            var = variables[var_name]
            
            for label in var.terms:
                ax.plot(
                    var.universe,
                    var[label].mf,
                    label=label, linewidth=1.5
                )
            
            if i < 4:
                ax.axvline(input_values[i], color=COLORS['text_dark'], linestyle='--', linewidth=2)
            else:
                ax.axvline(self.current_quality, color=COLORS['button_primary'], linestyle='--', linewidth=2, label='Wynik')
                
            ax.set_title(titles[i], fontsize=10)
            ax.set_xlabel(units[i], fontsize=8)
            ax.set_ylabel('Przynależność', fontsize=8)
            ax.legend(fontsize=7, loc='upper right')
            ax.grid(True, alpha=0.3)
        
        self.fig.tight_layout(pad=2.5) # Lepsze odstępy
        self.canvas_plot.draw()
    
    def _get_progress_bar_color(self, quality_value):
        """Określenie koloru paska na podstawie jakości"""
        if quality_value < 30:
            return "#C41E3A"  # Czerwony
        elif quality_value < 50:
            return "#FF6347"  # Pomarańczowy
        elif quality_value < 70:
            return "#FFD700"  # Żółty
        elif quality_value < 85:
            return "#90EE90"  # Jasnozielony
        else:
            return COLORS['button_primary'] # Kawowy brąz/zielony
            
    def _update_progress_bar(self, quality_value):
        """
        Aktualizacja paska postępu (zwiększona wysokość, gradient)
        """
        self.progress_canvas.delete("all")
        
        width = self.progress_canvas.winfo_width()
        if width <= 1:
            width = 600  # Domyślna szerokość
        
        height = 50 # Zwiększona wysokość
        
        # Tło paska
        self.progress_canvas.create_rectangle(
            0, 0, width, height,
            fill="#CCCCCC", outline=COLORS['text_dark'], width=2
        )
        
        # Wypełnienie proporcjonalne do jakości
        fill_width = (quality_value / 100.0) * width
        
        # Kolor wiodący dla gradientu
        start_color = self._get_progress_bar_color(quality_value)
        
        # Prosty gradient
        try:
            r, g, b = self.visualizer._hex_to_rgb(start_color)
            for i in range(int(fill_width)):
                # Zmiana jasności wzdłuż paska
                ratio = i / width
                r_step = int(r * (0.8 + 0.2 * ratio))
                g_step = int(g * (0.8 + 0.2 * ratio))
                b_step = int(b * (0.8 + 0.2 * ratio))
                gradient_color = f"#{r_step:02x}{g_step:02x}{b_step:02x}"
                self.progress_canvas.create_line(i, 0, i, height, fill=gradient_color, width=1)
        except ValueError:
             # Fallback na jednolity kolor
            self.progress_canvas.create_rectangle(
                0, 0, fill_width, height,
                fill=start_color, outline=""
            )
            
        # Rysowanie ikony filiżanki obok paska (opcjonalne)
        self.progress_canvas.create_text(
             fill_width + 20, height // 2,
             text="☕", font=('Arial', 24), anchor="w"
        )
        
    def _animate_progress_bar(self, target_value):
        """Animacja wypełniania paska postępu"""
        current = 0
        step = target_value / 20 # 20 kroków animacji
        
        def animate():
            nonlocal current
            if current < target_value:
                current += step
                # Ograniczenie do wartości docelowej
                progress = min(current, target_value)
                self._update_progress_bar(progress)
                self.root.after(30, animate)  # 30ms opóźnienia
            else:
                # Ostateczne ustawienie wartości na 100% dokładności
                self._update_progress_bar(target_value)
        
        animate()
    
    def evaluate_coffee(self):
        """Ocena kawy - główna funkcja wywoływana przyciskiem"""
        # Pobranie wartości z suwaków
        bitterness = self.bitterness_var.get()
        acidity = self.acidity_var.get()
        aroma = self.aroma_var.get()
        temperature = self.temperature_var.get()
        
        # Obliczenie jakości
        quality = self.fuzzy_system.evaluate(bitterness, acidity, aroma, temperature)
        self.current_quality = quality
        
        # Aktualizacja wizualizacji kubka
        self.visualizer.draw_cup(quality, temperature)
        
        # Aktualizacja wykresów
        self._update_plots()
        
        # Aktualizacja panelu wyniku (większy font)
        self.result_label.config(text=f"Wynik: {quality:.1f}/100")
        
        # Animacja paska postępu
        self._animate_progress_bar(quality)
        
        # Aktualizacja opisu
        quality_label = self.visualizer._get_quality_label(quality) # Używamy metody z Visualizer
        label_color = self.visualizer._get_label_color(quality)
        self.description_label.config(text=quality_label, fg=label_color)
    
    def reset_values(self):
        """Reset wszystkich wartości do domyślnych"""
        self.bitterness_var.set(5.0)
        self.acidity_var.set(5.0)
        self.aroma_var.set(5.0)
        self.temperature_var.set(80.0)
        
        self.current_quality = 0
        
        # Wyczyszczenie kubka
        self.visualizer.draw_cup(0, 60)
        
        # Reset wykresów
        self._initialize_plots()
        
        # Reset panelu wyniku
        self.result_label.config(text="Wynik: 0.0/100")
        self._update_progress_bar(0)
        self.description_label.config(text="", fg=COLORS['text_dark'])
    
    def run(self):
        """Uruchomienie aplikacji"""
        self.root.mainloop()