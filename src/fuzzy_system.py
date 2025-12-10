"""
System rozmyty do oceny jakości kawy - BrewSense
Implementacja logiki rozmytej z wykorzystaniem scikit-fuzzy
"""

import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl


class CoffeeQualitySystem:
    """
    Klasa implementująca system rozmyty do oceny jakości kawy.
    Wykorzystuje 4 zmienne wejściowe i 1 wyjściową.
    """
    
    def __init__(self):
        """Inicjalizacja systemu rozmytego z definicją zmiennych i reguł"""
        self._create_variables()
        self._create_membership_functions()
        self._create_rules()
        self._create_control_system()
    
    def _create_variables(self):
        """Tworzenie zmiennych wejściowych i wyjściowej"""
        
        # Zmienne wejściowe
        self.bitterness = ctrl.Antecedent(np.arange(0, 10.1, 0.1), 'bitterness')
        self.acidity = ctrl.Antecedent(np.arange(0, 10.1, 0.1), 'acidity')
        self.aroma = ctrl.Antecedent(np.arange(0, 10.1, 0.1), 'aroma')
        self.temperature = ctrl.Antecedent(np.arange(60, 95.1, 0.1), 'temperature')
        
        # Zmienna wyjściowa
        self.quality = ctrl.Consequent(np.arange(0, 100.1, 0.1), 'quality')
    
    def _create_membership_functions(self):
        """Definiowanie funkcji przynależności dla wszystkich zmiennych"""
        
        # Gorzkość (Bitterness)
        self.bitterness['low'] = fuzz.trapmf(self.bitterness.universe, [0, 0, 2, 4])
        self.bitterness['medium'] = fuzz.trimf(self.bitterness.universe, [2, 5, 8])
        self.bitterness['high'] = fuzz.trapmf(self.bitterness.universe, [6, 8, 10, 10])
        
        # Kwasowość (Acidity)
        self.acidity['low'] = fuzz.trapmf(self.acidity.universe, [0, 0, 2, 4])
        self.acidity['medium'] = fuzz.trimf(self.acidity.universe, [2, 5, 8])
        self.acidity['high'] = fuzz.trapmf(self.acidity.universe, [6, 8, 10, 10])
        
        # Aromat (Aroma)
        self.aroma['weak'] = fuzz.trapmf(self.aroma.universe, [0, 0, 2, 4])
        self.aroma['moderate'] = fuzz.trimf(self.aroma.universe, [3, 5, 7])
        self.aroma['strong'] = fuzz.trapmf(self.aroma.universe, [6, 8, 10, 10])
        
        # Temperatura (Temperature)
        self.temperature['low'] = fuzz.trapmf(self.temperature.universe, [60, 60, 70, 75])
        self.temperature['optimal'] = fuzz.trimf(self.temperature.universe, [72, 80, 88])
        self.temperature['high'] = fuzz.trapmf(self.temperature.universe, [85, 90, 95, 95])
        
        # Jakość (Quality)
        self.quality['very_poor'] = fuzz.trapmf(self.quality.universe, [0, 0, 15, 30])
        self.quality['poor'] = fuzz.trimf(self.quality.universe, [20, 35, 50])
        self.quality['average'] = fuzz.trimf(self.quality.universe, [40, 55, 70])
        self.quality['good'] = fuzz.trimf(self.quality.universe, [60, 75, 85])
        self.quality['very_good'] = fuzz.trimf(self.quality.universe, [75, 85, 95])
        self.quality['excellent'] = fuzz.trapmf(self.quality.universe, [85, 92, 100, 100])
    
    def _create_rules(self):
        """Tworzenie bazy reguł rozmytych (25 reguł)"""
        
        self.rules = [
            # Reguły dla wybitnej kawy (Excellent) - silny aromat, balans, optymalna temp
            ctrl.Rule(self.aroma['strong'] & self.bitterness['medium'] & 
                     self.acidity['medium'] & self.temperature['optimal'], 
                     self.quality['excellent']),
            
            ctrl.Rule(self.aroma['strong'] & self.bitterness['low'] & 
                     self.acidity['high'] & self.temperature['optimal'], 
                     self.quality['excellent']),
            
            ctrl.Rule(self.aroma['strong'] & self.bitterness['high'] & 
                     self.acidity['low'] & self.temperature['optimal'], 
                     self.quality['excellent']),
            
            # Reguły dla bardzo dobrej kawy (Very Good)
            ctrl.Rule(self.aroma['moderate'] & self.bitterness['medium'] & 
                     self.acidity['medium'] & self.temperature['optimal'], 
                     self.quality['very_good']),
            
            ctrl.Rule(self.aroma['strong'] & self.bitterness['medium'] & 
                     self.acidity['medium'] & self.temperature['high'], 
                     self.quality['very_good']),
            
            ctrl.Rule(self.aroma['strong'] & self.bitterness['low'] & 
                     self.acidity['medium'] & self.temperature['optimal'], 
                     self.quality['very_good']),
            
            ctrl.Rule(self.aroma['strong'] & self.bitterness['medium'] & 
                     self.acidity['low'] & self.temperature['optimal'], 
                     self.quality['very_good']),
            
            # Reguły dla dobrej kawy (Good)
            ctrl.Rule(self.aroma['moderate'] & self.bitterness['medium'] & 
                     self.acidity['low'] & self.temperature['optimal'], 
                     self.quality['good']),
            
            ctrl.Rule(self.aroma['moderate'] & self.bitterness['low'] & 
                     self.acidity['medium'] & self.temperature['optimal'], 
                     self.quality['good']),
            
            ctrl.Rule(self.aroma['strong'] & self.bitterness['medium'] & 
                     self.acidity['medium'] & self.temperature['low'], 
                     self.quality['good']),
            
            ctrl.Rule(self.aroma['moderate'] & self.bitterness['medium'] & 
                     self.acidity['medium'] & self.temperature['high'], 
                     self.quality['good']),
            
            ctrl.Rule(self.aroma['strong'] & self.bitterness['high'] & 
                     self.acidity['high'] & self.temperature['optimal'], 
                     self.quality['good']),
            
            # Reguły dla średniej kawy (Average)
            ctrl.Rule(self.aroma['moderate'] & self.bitterness['low'] & 
                     self.acidity['low'] & self.temperature['optimal'], 
                     self.quality['average']),
            
            ctrl.Rule(self.aroma['weak'] & self.bitterness['medium'] & 
                     self.acidity['medium'] & self.temperature['optimal'], 
                     self.quality['average']),
            
            ctrl.Rule(self.aroma['moderate'] & self.bitterness['high'] & 
                     self.acidity['medium'] & self.temperature['optimal'], 
                     self.quality['average']),
            
            ctrl.Rule(self.aroma['moderate'] & self.bitterness['medium'] & 
                     self.acidity['high'] & self.temperature['high'], 
                     self.quality['average']),
            
            ctrl.Rule(self.aroma['moderate'] & self.bitterness['medium'] & 
                     self.acidity['medium'] & self.temperature['low'], 
                     self.quality['average']),
            
            # Reguły dla słabej kawy (Poor)
            ctrl.Rule(self.aroma['weak'] & self.bitterness['high'] & 
                     self.acidity['low'] & self.temperature['optimal'], 
                     self.quality['poor']),
            
            ctrl.Rule(self.aroma['weak'] & self.bitterness['low'] & 
                     self.acidity['high'] & self.temperature['optimal'], 
                     self.quality['poor']),
            
            ctrl.Rule(self.aroma['moderate'] & self.bitterness['high'] & 
                     self.acidity['high'] & self.temperature['low'], 
                     self.quality['poor']),
            
            ctrl.Rule(self.aroma['weak'] & self.bitterness['medium'] & 
                     self.acidity['medium'] & self.temperature['low'], 
                     self.quality['poor']),
            
            # Reguły dla bardzo słabej kawy (Very Poor)
            ctrl.Rule(self.aroma['weak'] & self.bitterness['high'] & 
                     self.acidity['high'] & self.temperature['optimal'], 
                     self.quality['very_poor']),
            
            ctrl.Rule(self.aroma['weak'] & self.bitterness['low'] & 
                     self.acidity['low'] & self.temperature['low'], 
                     self.quality['very_poor']),
            
            ctrl.Rule(self.aroma['weak'] & self.bitterness['high'] & 
                     self.acidity['low'] & self.temperature['high'], 
                     self.quality['very_poor']),
            
            ctrl.Rule(self.aroma['weak'] & self.bitterness['high'] & 
                     self.acidity['high'] & self.temperature['low'], 
                     self.quality['very_poor']),
        ]
    
    def _create_control_system(self):
        """Tworzenie systemu kontroli i symulatora"""
        self.control_system = ctrl.ControlSystem(self.rules)
        self.simulator = ctrl.ControlSystemSimulation(self.control_system)
    
    def evaluate(self, bitterness_val, acidity_val, aroma_val, temperature_val):
        """
        Ocena jakości kawy na podstawie parametrów wejściowych
        
        Args:
            bitterness_val (float): Gorzkość (0-10)
            acidity_val (float): Kwasowość (0-10)
            aroma_val (float): Aromat (0-10)
            temperature_val (float): Temperatura (60-95°C)
        
        Returns:
            float: Jakość kawy (0-100)
        """
        try:
            # Ustawienie wartości wejściowych
            self.simulator.input['bitterness'] = bitterness_val
            self.simulator.input['acidity'] = acidity_val
            self.simulator.input['aroma'] = aroma_val
            self.simulator.input['temperature'] = temperature_val
            
            # Obliczenie wyniku
            self.simulator.compute()
            
            # Zwrócenie wyniku
            return self.simulator.output['quality']
        
        except Exception as e:
            print(f"Błąd podczas obliczania jakości: {e}")
            return 50.0  # Wartość domyślna w przypadku błędu
    
    def get_quality_label(self, quality_value):
        """
        Określenie etykiety słownej dla wartości jakości
        
        Args:
            quality_value (float): Wartość jakości (0-100)
        
        Returns:
            str: Etykieta słowna jakości
        """
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
    
    def get_variables(self):
        """
        Zwraca słownik ze wszystkimi zmiennymi systemu
        
        Returns:
            dict: Słownik zmiennych (antecedent i consequent)
        """
        return {
            'bitterness': self.bitterness,
            'acidity': self.acidity,
            'aroma': self.aroma,
            'temperature': self.temperature,
            'quality': self.quality
        }