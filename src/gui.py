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
from fuzzy_system import CoffeeQualitySystem


class CoffeeVisualizer:
    """Klasa odpowiedzialna za rysowanie wizualizacji kubka kawy"""
    
    def __init__(self, canvas):
        """
        Inicjalizacja wizualizera
        
        Args:
            canvas: Widget Canvas z tkinter
        """
        self.canvas = canvas
        self.canvas_width = 350
        self.canvas_height = 400
    
    def draw_cup(self, quality_value, temperature_val):
        """
        Rysowanie kubka z kawą
        
        Args:
            quality_value (float): Jakość kawy (0-100)
            temperature_val (float): Temperatura kawy (60-95°C)
        """
        # Czyszczenie canvas
        self.canvas.delete("all")
        
        # Parametry kubka
        cup_bottom_y = 320
        cup_top_y = 150
        cup_height = cup_bottom_y - cup_top_y
        cup_bottom_width = 120
        cup_top_width = 140
        center_x = self.canvas_width // 2
        
        # Obliczenie pozycji kubka
        left_bottom = center_x - cup_bottom_width // 2
        right_bottom = center_x + cup_bottom_width // 2
        left_top = center_x - cup_top_width // 2
        right_top = center_x + cup_top_width // 2
        
        # Rysowanie spodka
        spodek_y = cup_bottom_y + 10
        self.canvas.create_oval(
            center_x - 90, spodek_y,
            center_x + 90, spodek_y + 20,
            fill="#8B7355", outline="#654321", width=2
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
            fill="#F5F5DC", outline="#8B7355", width=3
        )
        
        # Rysowanie uchwytu
        handle_x = right_top + 10
        handle_y_top = cup_top_y + 30
        handle_y_bottom = cup_top_y + 90
        
        self.canvas.create_arc(
            handle_x, handle_y_top,
            handle_x + 40, handle_y_bottom,
            start=270, extent=180, style=tk.ARC,
            outline="#8B7355", width=3
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
            ellipse_width = coffee_right - coffee_left
            self.canvas.create_oval(
                coffee_left, coffee_level - 5,
                coffee_right, coffee_level + 10,
                fill=self._darken_color(coffee_color), outline=""
            )
        
        # Rysowanie pary (jeśli temperatura > 75°C)
        if temperature_val > 75:
            self._draw_steam(center_x, cup_top_y - 10)
        
        # Rysowanie wyniku pod kubkiem
        quality_label = self._get_quality_label(quality_value)
        
        # Wartość numeryczna
        self.canvas.create_text(
            center_x, cup_bottom_y + 50,
            text=f"{quality_value:.1f}/100",
            font=("Arial", 24, "bold"),
            fill="#2F1E15"
        )
        
        # Etykieta słowna
        label_color = self._get_label_color(quality_value)
        self.canvas.create_text(
            center_x, cup_bottom_y + 80,
            text=quality_label,
            font=("Arial", 18, "bold"),
            fill=label_color
        )
    
    def _draw_steam(self, center_x, start_y):
        """Rysowanie pary nad kubkiem"""
        steam_color = "#D3D3D3"
        
        # Trzy fale pary
        for i in range(3):
            x_offset = -20 + i * 20
            y_offset = i * 15
            
            # Fala jako krzywa
            points = []
            for t in np.linspace(0, 1, 20):
                x = center_x + x_offset + np.sin(t * 3.14 * 2) * 8
                y = start_y - y_offset - t * 30
                points.extend([x, y])
            
            self.canvas.create_line(
                points,
                smooth=True, width=2, fill=steam_color
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
            return "#2F1E15"  # Prawie czarny
    
    def _darken_color(self, color):
        """Przyciemnienie koloru (dla efektu 3D)"""
        # Prosta metoda przyciemniania przez zmniejszenie wartości RGB
        rgb = self.canvas.winfo_rgb(color)
        darker_rgb = tuple(int(c * 0.7) for c in rgb)
        return f"#{darker_rgb[0]//256:02x}{darker_rgb[1]//256:02x}{darker_rgb[2]//256:02x}"
    
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
        """Określenie koloru etykiety na podstawie jakości"""
        if quality_value < 30:
            return "#C41E3A"  # Czerwony
        elif quality_value < 50:
            return "#FF6347"  # Pomarańczowo-czerwony
        elif quality_value < 70:
            return "#FFD700"  # Złoty
        elif quality_value < 85:
            return "#90EE90"  # Jasnozielony
        else:
            return "#228B22"  # Ciemnozielony
    
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
        self.root.geometry("1400x900")
        self.root.resizable(False, False)
        
        # Inicjalizacja systemu rozmytego
        self.fuzzy_system = CoffeeQualitySystem()
        
        # Wartości domyślne
        self.current_quality = 0
        
        # Tworzenie interfejsu
        self._create_widgets()
        
    def _create_widgets(self):
        """Tworzenie wszystkich widgetów GUI"""
        
        # Główny frame
        main_frame = tk.Frame(self.root, bg="#F0F0F0")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
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
        left_frame = tk.Frame(parent, bg="#E8E8E8", padx=20, pady=20)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # Tytuł
        title = tk.Label(
            left_frame, text="Parametry Kawy",
            font=("Arial", 16, "bold"), bg="#E8E8E8"
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
            self.bitterness_var, 0, 10, ""
        )
        
        # Kwasowość
        self._create_slider(
            left_frame, "Kwasowość (Acidity):",
            self.acidity_var, 0, 10, ""
        )
        
        # Aromat
        self._create_slider(
            left_frame, "Aromat (Aroma):",
            self.aroma_var, 0, 10, ""
        )
        
        # Temperatura
        self._create_slider(
            left_frame, "Temperatura (Temperature):",
            self.temperature_var, 60, 95, "°C"
        )
        
        # Przyciski
        button_frame = tk.Frame(left_frame, bg="#E8E8E8")
        button_frame.pack(pady=30)
        
        evaluate_btn = tk.Button(
            button_frame, text="Oceń Kawę",
            font=("Arial", 14, "bold"),
            bg="#4CAF50", fg="white",
            padx=30, pady=10,
            command=self.evaluate_coffee
        )
        evaluate_btn.pack(pady=5)
        
        reset_btn = tk.Button(
            button_frame, text="Reset",
            font=("Arial", 12),
            bg="#FF6347", fg="white",
            padx=30, pady=8,
            command=self.reset_values
        )
        reset_btn.pack(pady=5)
    
    def _create_slider(self, parent, label_text, variable, from_, to, unit):
        """
        Tworzenie suwaka z etykietą
        
        Args:
            parent: Widget rodzica
            label_text (str): Tekst etykiety
            variable: Zmienna tkinter
            from_ (float): Wartość minimalna
            to (float): Wartość maksymalna
            unit (str): Jednostka (np. "°C")
        """
        frame = tk.Frame(parent, bg="#E8E8E8")
        frame.pack(fill=tk.X, pady=10)
        
        # Etykieta
        label = tk.Label(
            frame, text=label_text,
            font=("Arial", 11), bg="#E8E8E8"
        )
        label.pack(anchor="w")
        
        # Frame dla suwaka i wartości
        slider_frame = tk.Frame(frame, bg="#E8E8E8")
        slider_frame.pack(fill=tk.X, pady=5)
        
        # Suwak
        slider = tk.Scale(
            slider_frame, from_=from_, to=to,
            orient=tk.HORIZONTAL, variable=variable,
            resolution=0.1, length=200,
            bg="#E8E8E8", troughcolor="#CCCCCC"
        )
        slider.pack(side=tk.LEFT)
        
        # Etykieta z wartością
        value_label = tk.Label(
            slider_frame, text=f"{variable.get():.1f}{unit}",
            font=("Arial", 11, "bold"), bg="#E8E8E8", width=8
        )
        value_label.pack(side=tk.LEFT, padx=10)
        
        # Aktualizacja wartości przy zmianie
        def update_value(*args):
            value_label.config(text=f"{variable.get():.1f}{unit}")
        
        variable.trace('w', update_value)
    
    def _create_middle_panel(self, parent):
        """Tworzenie środkowego panelu z wykresami"""
        middle_frame = tk.Frame(parent, bg="#FFFFFF", padx=10, pady=10)
        middle_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        
        # Tytuł
        title = tk.Label(
            middle_frame, text="Wykresy Funkcji Przynależności",
            font=("Arial", 14, "bold"), bg="#FFFFFF"
        )
        title.pack(pady=(0, 10))
        
        # Figure dla wykresów
        self.fig = Figure(figsize=(8, 10), dpi=80)
        self.canvas_plot = FigureCanvasTkAgg(self.fig, master=middle_frame)
        self.canvas_plot.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Początkowe puste wykresy
        self._initialize_plots()
    
    def _create_right_panel(self, parent):
        """Tworzenie prawego panelu z wizualizacją kubka"""
        right_frame = tk.Frame(parent, bg="#FFFFFF", padx=20, pady=20)
        right_frame.grid(row=0, column=2, sticky="nsew", padx=10, pady=10)
        
        # Tytuł
        title = tk.Label(
            right_frame, text="Wizualizacja Jakości",
            font=("Arial", 14, "bold"), bg="#FFFFFF"
        )
        title.pack(pady=(0, 20))
        
        # Canvas dla kubka
        self.cup_canvas = tk.Canvas(
            right_frame, width=350, height=400,
            bg="#FFFFFF", highlightthickness=0
        )
        self.cup_canvas.pack()
        
        # Inicjalizacja wizualizera
        self.visualizer = CoffeeVisualizer(self.cup_canvas)
        self.visualizer.draw_cup(0, 60)
    
    def _create_bottom_panel(self, parent):
        """Tworzenie dolnego panelu z wynikiem"""
        bottom_frame = tk.Frame(parent, bg="#E8E8E8", padx=20, pady=15)
        bottom_frame.grid(row=1, column=0, columnspan=3, sticky="ew", padx=10, pady=10)
        
        # Etykieta wyniku
        self.result_label = tk.Label(
            bottom_frame, text="Wynik: 0.0/100",
            font=("Arial", 24, "bold"), bg="#E8E8E8"
        )
        self.result_label.pack(side=tk.LEFT, padx=20)
        
        # Pasek postępu
        self.progress_frame = tk.Frame(bottom_frame, bg="#E8E8E8")
        self.progress_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=20)
        
        self.progress_canvas = tk.Canvas(
            self.progress_frame, height=40, bg="#E8E8E8",
            highlightthickness=0
        )
        self.progress_canvas.pack(fill=tk.X)
        
        # Etykieta opisu
        self.description_label = tk.Label(
            bottom_frame, text="",
            font=("Arial", 18, "bold"), bg="#E8E8E8"
        )
        self.description_label.pack(side=tk.LEFT, padx=20)
        
        # Początkowy pasek postępu
        self._update_progress_bar(0)
        
        # Konfiguracja siatki
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(1, weight=1)
    
    def _initialize_plots(self):
        """Inicjalizacja pustych wykresów"""
        self.fig.clear()
        
        # 5 subplotów (4 dla wejść, 1 dla wyjścia)
        self.ax1 = self.fig.add_subplot(5, 1, 1)
        self.ax2 = self.fig.add_subplot(5, 1, 2)
        self.ax3 = self.fig.add_subplot(5, 1, 3)
        self.ax4 = self.fig.add_subplot(5, 1, 4)
        self.ax5 = self.fig.add_subplot(5, 1, 5)
        
        self.fig.tight_layout(pad=2.0)
        self.canvas_plot.draw()
    
    def _update_plots(self):
        """Aktualizacja wykresów po obliczeniu"""
        self.fig.clear()
        
        variables = self.fuzzy_system.get_variables()
        
        # Subplot 1: Gorzkość
        ax1 = self.fig.add_subplot(5, 1, 1)
        for label in variables['bitterness'].terms:
            ax1.plot(
                variables['bitterness'].universe,
                variables['bitterness'][label].mf,
                label=label, linewidth=1.5
            )
        ax1.axvline(self.bitterness_var.get(), color='r', linestyle='--', linewidth=2)
        ax1.set_title('Gorzkość (Bitterness)', fontsize=10)
        ax1.set_xlabel('Wartość', fontsize=8)
        ax1.set_ylabel('Przynależność', fontsize=8)
        ax1.legend(fontsize=7, loc='upper right')
        ax1.grid(True, alpha=0.3)
        
        # Subplot 2: Kwasowość
        ax2 = self.fig.add_subplot(5, 1, 2)
        for label in variables['acidity'].terms:
            ax2.plot(
                variables['acidity'].universe,
                variables['acidity'][label].mf,
                label=label, linewidth=1.5
            )
        ax2.axvline(self.acidity_var.get(), color='r', linestyle='--', linewidth=2)
        ax2.set_title('Kwasowość (Acidity)', fontsize=10)
        ax2.set_xlabel('Wartość', fontsize=8)
        ax2.set_ylabel('Przynależność', fontsize=8)
        ax2.legend(fontsize=7, loc='upper right')
        ax2.grid(True, alpha=0.3)
        
        # Subplot 3: Aromat
        ax3 = self.fig.add_subplot(5, 1, 3)
        for label in variables['aroma'].terms:
            ax3.plot(
                variables['aroma'].universe,
                variables['aroma'][label].mf,
                label=label, linewidth=1.5
            )
        ax3.axvline(self.aroma_var.get(), color='r', linestyle='--', linewidth=2)
        ax3.set_title('Aromat (Aroma)', fontsize=10)
        ax3.set_xlabel('Wartość', fontsize=8)
        ax3.set_ylabel('Przynależność', fontsize=8)
        ax3.legend(fontsize=7, loc='upper right')
        ax3.grid(True, alpha=0.3)
        
        # Subplot 4: Temperatura
        ax4 = self.fig.add_subplot(5, 1, 4)
        for label in variables['temperature'].terms:
            ax4.plot(
                variables['temperature'].universe,
                variables['temperature'][label].mf,
                label=label, linewidth=1.5
            )
        ax4.axvline(self.temperature_var.get(), color='r', linestyle='--', linewidth=2)
        ax4.set_title('Temperatura (Temperature)', fontsize=10)
        ax4.set_xlabel('°C', fontsize=8)
        ax4.set_ylabel('Przynależność', fontsize=8)
        ax4.legend(fontsize=7, loc='upper right')
        ax4.grid(True, alpha=0.3)
        
        # Subplot 5: Jakość (z defuzzyfikacją)
        ax5 = self.fig.add_subplot(5, 1, 5)
        for label in variables['quality'].terms:
            ax5.plot(
                variables['quality'].universe,
                variables['quality'][label].mf,
                label=label, linewidth=1.5, alpha=0.7
            )
        ax5.axvline(self.current_quality, color='r', linestyle='--', linewidth=2, label='Wynik')
        ax5.set_title('Jakość (Quality) - Defuzzyfikacja', fontsize=10)
        ax5.set_xlabel('Wartość (0-100)', fontsize=8)
        ax5.set_ylabel('Przynależność', fontsize=8)
        ax5.legend(fontsize=7, loc='upper right')
        ax5.grid(True, alpha=0.3)
        
        self.fig.tight_layout(pad=1.5)
        self.canvas_plot.draw()
    
    def _update_progress_bar(self, quality_value):
        """
        Aktualizacja paska postępu
        
        Args:
            quality_value (float): Wartość jakości (0-100)
        """
        self.progress_canvas.delete("all")
        
        width = self.progress_canvas.winfo_width()
        if width <= 1:
            width = 600  # Domyślna szerokość
        
        height = 40
        
        # Tło paska
        self.progress_canvas.create_rectangle(
            0, 0, width, height,
            fill="#CCCCCC", outline="#999999", width=2
        )
        
        # Wypełnienie proporcjonalne do jakości
        fill_width = (quality_value / 100.0) * width
        
        # Kolor zależny od jakości
        if quality_value < 30:
            color = "#C41E3A"  # Czerwony
        elif quality_value < 50:
            color = "#FF6347"  # Pomarańczowy
        elif quality_value < 70:
            color = "#FFD700"  # Żółty
        elif quality_value < 85:
            color = "#90EE90"  # Jasnozielony
        else:
            color = "#228B22"  # Ciemnozielony
        
        self.progress_canvas.create_rectangle(
            0, 0, fill_width, height,
            fill=color, outline=""
        )
    
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
        
        # Aktualizacja panelu wyniku
        self.result_label.config(text=f"Wynik: {quality:.1f}/100")
        self._update_progress_bar(quality)
        
        # Aktualizacja opisu
        quality_label = self.fuzzy_system.get_quality_label(quality)
        label_color = self._get_description_color(quality)
        self.description_label.config(text=quality_label, fg=label_color)
    
    def _get_description_color(self, quality_value):
        """Określenie koloru opisu na podstawie jakości"""
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
        self.description_label.config(text="")
    
    def run(self):
        """Uruchomienie aplikacji"""
        self.root.mainloop()