"""
System rozmyty do oceny jakości kawy - BrewSense
Implementacja logiki rozmytej z wykorzystaniem scikit-fuzzy
Wersja z rozszerzonymi logami debugowania
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
        
        # Zmienna wyjściowa z wartością domyślną
        # Jeśli żadna reguła nie zostanie aktywowana, zwróci 25.0 (very_poor)
        self.quality = ctrl.Consequent(np.arange(0, 100.1, 0.1), 'quality', defuzzify_method='centroid')
        self.quality.defuzzify_method = 'centroid'
        
        # Ustawienie wartości domyślnej (używanej gdy brak aktywacji reguł)
        # UWAGA: Ta funkcjonalność działa od wersji scikit-fuzzy 0.4.0+
        try:
            self.quality.default_value = 25.0  # Bardzo słaba kawa jako default
        except AttributeError:
            # Starsza wersja scikit-fuzzy nie obsługuje default_value
            pass
    
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
        """Tworzenie bazy reguł rozmytych (42 reguły + reguły catch-all)"""
        
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
            
            ctrl.Rule(self.aroma['weak'] & self.bitterness['low'] & 
                     self.acidity['low'] & self.temperature['high'], 
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
            
            ctrl.Rule(self.aroma['weak'] & self.bitterness['high'] & 
                     self.acidity['high'] & self.temperature['high'], 
                     self.quality['very_poor']),
            
            # REGUŁY DOMYŚLNE (FALLBACK) - dla przypadków brzegowych
            # Brak aromatu = zawsze bardzo słaba kawa
            ctrl.Rule(self.aroma['weak'] & self.bitterness['low'] & 
                     self.acidity['low'] & self.temperature['optimal'], 
                     self.quality['very_poor']),
            
            ctrl.Rule(self.aroma['weak'] & self.bitterness['medium'] & 
                     self.acidity['low'] & self.temperature['optimal'], 
                     self.quality['very_poor']),
            
            ctrl.Rule(self.aroma['weak'] & self.bitterness['low'] & 
                     self.acidity['medium'] & self.temperature['optimal'], 
                     self.quality['poor']),
            
            ctrl.Rule(self.aroma['weak'] & self.bitterness['medium'] & 
                     self.acidity['high'] & self.temperature['optimal'], 
                     self.quality['poor']),
            
            ctrl.Rule(self.aroma['weak'] & self.bitterness['high'] & 
                     self.acidity['medium'] & self.temperature['optimal'], 
                     self.quality['poor']),
            
            # Dodatkowe reguły dla skrajnych temperatur
            ctrl.Rule(self.aroma['weak'] & self.bitterness['low'] & 
                     self.acidity['medium'] & self.temperature['high'], 
                     self.quality['poor']),
            
            ctrl.Rule(self.aroma['weak'] & self.bitterness['medium'] & 
                     self.acidity['low'] & self.temperature['low'], 
                     self.quality['very_poor']),
            
            # ===================================================================
            # REGUŁY UNIWERSALNE (CATCH-ALL) - dla wszystkich pozostałych przypadków
            # Te reguły używają operatora OR (~) aby złapać przypadki nie objęte innymi regułami
            # ===================================================================
            
            # Jeśli aromat słaby, niezależnie od reszty - słaba/bardzo słaba kawa
            ctrl.Rule(self.aroma['weak'] & self.temperature['low'], 
                     self.quality['very_poor']),
            
            ctrl.Rule(self.aroma['weak'] & self.temperature['high'], 
                     self.quality['poor']),
            
            # Jeśli aromat słaby i temperatura optymalna - słaba kawa (catch-all)
            # Ta reguła złapie wszystkie przypadki weak aroma + optimal temp
            ctrl.Rule(self.aroma['weak'] & self.temperature['optimal'], 
                     self.quality['poor']),
            
            # Dla średniego aromatu - średnia kawa (catch-all)
            ctrl.Rule(self.aroma['moderate'] & self.temperature['low'], 
                     self.quality['poor']),
            
            ctrl.Rule(self.aroma['moderate'] & self.temperature['high'], 
                     self.quality['average']),
            
            # Dla silnego aromatu ale skrajnych temperatur
            ctrl.Rule(self.aroma['strong'] & self.temperature['low'], 
                     self.quality['average']),
            
            ctrl.Rule(self.aroma['strong'] & self.temperature['high'], 
                     self.quality['good']),
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
        print("\n" + "="*70)
        print("ROZPOCZĘCIE OCENY KAWY - FUZZY SYSTEM LOG")
        print("="*70)
        
        try:
            # Walidacja i logowanie wartości wejściowych
            print("\n[1] WARTOŚCI WEJŚCIOWE:")
            print(f"    Gorzkość (Bitterness):  {bitterness_val:.2f}")
            print(f"    Kwasowość (Acidity):    {acidity_val:.2f}")
            print(f"    Aromat (Aroma):         {aroma_val:.2f}")
            print(f"    Temperatura:            {temperature_val:.2f}°C")
            
            # Sprawdzenie zakresów
            print("\n[2] WALIDACJA ZAKRESÓW:")
            valid = True
            if not (0 <= bitterness_val <= 10):
                print(f"    ⚠️  UWAGA: Gorzkość poza zakresem [0-10]: {bitterness_val}")
                bitterness_val = max(0, min(10, bitterness_val))
                print(f"    ✓  Skorygowano do: {bitterness_val}")
                valid = False
            else:
                print(f"    ✓  Gorzkość w zakresie")
                
            if not (0 <= acidity_val <= 10):
                print(f"    ⚠️  UWAGA: Kwasowość poza zakresem [0-10]: {acidity_val}")
                acidity_val = max(0, min(10, acidity_val))
                print(f"    ✓  Skorygowano do: {acidity_val}")
                valid = False
            else:
                print(f"    ✓  Kwasowość w zakresie")
                
            if not (0 <= aroma_val <= 10):
                print(f"    ⚠️  UWAGA: Aromat poza zakresem [0-10]: {aroma_val}")
                aroma_val = max(0, min(10, aroma_val))
                print(f"    ✓  Skorygowano do: {aroma_val}")
                valid = False
            else:
                print(f"    ✓  Aromat w zakresie")
                
            if not (60 <= temperature_val <= 95):
                print(f"    ⚠️  UWAGA: Temperatura poza zakresem [60-95]: {temperature_val}")
                temperature_val = max(60, min(95, temperature_val))
                print(f"    ✓  Skorygowano do: {temperature_val}")
                valid = False
            else:
                print(f"    ✓  Temperatura w zakresie")
            
            if valid:
                print("    ✓  Wszystkie wartości w poprawnych zakresach")
            
            # Ustawienie wartości wejściowych
            print("\n[3] USTAWIANIE WARTOŚCI W SYMULATORZE:")
            self.simulator.input['bitterness'] = bitterness_val
            print(f"    ✓  Ustawiono gorzkość: {bitterness_val}")
            
            self.simulator.input['acidity'] = acidity_val
            print(f"    ✓  Ustawiono kwasowość: {acidity_val}")
            
            self.simulator.input['aroma'] = aroma_val
            print(f"    ✓  Ustawiono aromat: {aroma_val}")
            
            self.simulator.input['temperature'] = temperature_val
            print(f"    ✓  Ustawiono temperaturę: {temperature_val}")
            
            # Obliczenie wyniku
            print("\n[4] OBLICZANIE WYJŚCIA (DEFUZZYFIKACJA):")
            print("    Uruchamianie systemu rozmytego...")
            
            # DIAGNOSTYKA - sprawdzenie aktywacji przed compute()
            print("\n    [DIAGNOSTYKA] Sprawdzanie stopni przynależności przed obliczeniem:")
            self._check_rule_activation(bitterness_val, acidity_val, aroma_val, temperature_val)
            
            try:
                self.simulator.compute()
                print("    ✓  Obliczenia zakończone pomyślnie")
            except KeyError as e:
                print(f"\n    ⚠️  Brak aktywacji reguł dla danych wejściowych!")
                print(f"    System nie może obliczyć wartości - używam wartości domyślnej")
                # Zwróć wartość domyślną dla bardzo słabej kawy
                return 25.0
            
            # Sprawdzenie czy wynik istnieje
            if 'quality' not in self.simulator.output:
                print("\n    ⚠️  UWAGA: Brak klucza 'quality' w output!")
                print(f"    Dostępne klucze: {list(self.simulator.output.keys())}")
                print("    Zwracam wartość domyślną: 25.0")
                return 25.0
            
            # Pobranie wyniku
            quality_result = self.simulator.output['quality']
            print(f"\n[5] WYNIK:")
            print(f"    Jakość kawy: {quality_result:.2f}/100")
            
            # Określenie kategorii
            quality_label = self.get_quality_label(quality_result)
            print(f"    Kategoria: {quality_label}")
            
            # Szczegółowa analiza aktywacji reguł (opcjonalna)
            print("\n[6] DODATKOWE INFORMACJE:")
            self._log_activation_details(bitterness_val, acidity_val, aroma_val, temperature_val)
            
            print("\n" + "="*70)
            print("ZAKOŃCZENIE OCENY - SUKCES")
            print("="*70 + "\n")
            
            return quality_result
        
        except Exception as e:
            print("\n" + "!"*70)
            print("BŁĄD PODCZAS OBLICZANIA JAKOŚCI")
            print("!"*70)
            print(f"\nTyp błędu: {type(e).__name__}")
            print(f"Komunikat: {str(e)}")
            print(f"\nWartości wejściowe w momencie błędu:")
            print(f"  - Gorzkość: {bitterness_val}")
            print(f"  - Kwasowość: {acidity_val}")
            print(f"  - Aromat: {aroma_val}")
            print(f"  - Temperatura: {temperature_val}")
            
            # Szczegółowy stack trace
            import traceback
            print("\nPełny stack trace:")
            traceback.print_exc()
            
            print("\n" + "!"*70)
            print("ZWRACANIE WARTOŚCI DOMYŚLNEJ: 50.0")
            print("!"*70 + "\n")
            
            return 50.0  # Wartość domyślna w przypadku błędu
    
    def _check_rule_activation(self, bitterness_val, acidity_val, aroma_val, temperature_val):
        """
        Sprawdzenie czy jakiekolwiek reguły zostaną aktywowane
        
        Args:
            bitterness_val (float): Wartość gorzkości
            acidity_val (float): Wartość kwasowości
            aroma_val (float): Wartość aromatu
            temperature_val (float): Wartość temperatury
        """
        try:
            # Obliczenie stopni przynależności
            bit_low = fuzz.interp_membership(self.bitterness.universe, self.bitterness['low'].mf, bitterness_val)
            bit_med = fuzz.interp_membership(self.bitterness.universe, self.bitterness['medium'].mf, bitterness_val)
            bit_high = fuzz.interp_membership(self.bitterness.universe, self.bitterness['high'].mf, bitterness_val)
            
            aci_low = fuzz.interp_membership(self.acidity.universe, self.acidity['low'].mf, acidity_val)
            aci_med = fuzz.interp_membership(self.acidity.universe, self.acidity['medium'].mf, acidity_val)
            aci_high = fuzz.interp_membership(self.acidity.universe, self.acidity['high'].mf, acidity_val)
            
            aro_weak = fuzz.interp_membership(self.aroma.universe, self.aroma['weak'].mf, aroma_val)
            aro_mod = fuzz.interp_membership(self.aroma.universe, self.aroma['moderate'].mf, aroma_val)
            aro_strong = fuzz.interp_membership(self.aroma.universe, self.aroma['strong'].mf, aroma_val)
            
            temp_low = fuzz.interp_membership(self.temperature.universe, self.temperature['low'].mf, temperature_val)
            temp_opt = fuzz.interp_membership(self.temperature.universe, self.temperature['optimal'].mf, temperature_val)
            temp_high = fuzz.interp_membership(self.temperature.universe, self.temperature['high'].mf, temperature_val)
            
            # Sprawdzenie maksymalnych wartości
            max_activations = {
                'bitterness': max(bit_low, bit_med, bit_high),
                'acidity': max(aci_low, aci_med, aci_high),
                'aroma': max(aro_weak, aro_mod, aro_strong),
                'temperature': max(temp_low, temp_opt, temp_high)
            }
            
            print(f"      Maksymalne stopnie przynależności:")
            for var, val in max_activations.items():
                status = "✓" if val > 0 else "⚠️"
                print(f"        {status} {var}: {val:.3f}")
            
            # Sprawdzenie czy wszystkie zmienne mają jakąś aktywację
            all_active = all(val > 0 for val in max_activations.values())
            
            if not all_active:
                print("\n      ⚠️  OSTRZEŻENIE: Niektóre zmienne nie mają aktywacji!")
                print("      To może prowadzić do braku aktywacji reguł.")
            else:
                print("\n      ✓  Wszystkie zmienne mają aktywację > 0")
                
        except Exception as e:
            print(f"      ⚠️  Błąd podczas diagnostyki: {e}")
    
    def _log_activation_details(self, bitterness_val, acidity_val, aroma_val, temperature_val):
        """
        Logowanie szczegółów aktywacji funkcji przynależności
        
        Args:
            bitterness_val (float): Wartość gorzkości
            acidity_val (float): Wartość kwasowości
            aroma_val (float): Wartość aromatu
            temperature_val (float): Wartość temperatury
        """
        try:
            print("    Stopnie przynależności dla wartości wejściowych:")
            
            # Gorzkość
            print(f"\n    Gorzkość ({bitterness_val:.2f}):")
            bit_low = fuzz.interp_membership(self.bitterness.universe, self.bitterness['low'].mf, bitterness_val)
            bit_med = fuzz.interp_membership(self.bitterness.universe, self.bitterness['medium'].mf, bitterness_val)
            bit_high = fuzz.interp_membership(self.bitterness.universe, self.bitterness['high'].mf, bitterness_val)
            print(f"      - low:    {bit_low:.3f}")
            print(f"      - medium: {bit_med:.3f}")
            print(f"      - high:   {bit_high:.3f}")
            
            # Kwasowość
            print(f"\n    Kwasowość ({acidity_val:.2f}):")
            aci_low = fuzz.interp_membership(self.acidity.universe, self.acidity['low'].mf, acidity_val)
            aci_med = fuzz.interp_membership(self.acidity.universe, self.acidity['medium'].mf, acidity_val)
            aci_high = fuzz.interp_membership(self.acidity.universe, self.acidity['high'].mf, acidity_val)
            print(f"      - low:    {aci_low:.3f}")
            print(f"      - medium: {aci_med:.3f}")
            print(f"      - high:   {aci_high:.3f}")
            
            # Aromat
            print(f"\n    Aromat ({aroma_val:.2f}):")
            aro_weak = fuzz.interp_membership(self.aroma.universe, self.aroma['weak'].mf, aroma_val)
            aro_mod = fuzz.interp_membership(self.aroma.universe, self.aroma['moderate'].mf, aroma_val)
            aro_strong = fuzz.interp_membership(self.aroma.universe, self.aroma['strong'].mf, aroma_val)
            print(f"      - weak:     {aro_weak:.3f}")
            print(f"      - moderate: {aro_mod:.3f}")
            print(f"      - strong:   {aro_strong:.3f}")
            
            # Temperatura
            print(f"\n    Temperatura ({temperature_val:.2f}°C):")
            temp_low = fuzz.interp_membership(self.temperature.universe, self.temperature['low'].mf, temperature_val)
            temp_opt = fuzz.interp_membership(self.temperature.universe, self.temperature['optimal'].mf, temperature_val)
            temp_high = fuzz.interp_membership(self.temperature.universe, self.temperature['high'].mf, temperature_val)
            print(f"      - low:     {temp_low:.3f}")
            print(f"      - optimal: {temp_opt:.3f}")
            print(f"      - high:    {temp_high:.3f}")
            
            # Identyfikacja dominujących wartości
            print("\n    Dominujące kategorie:")
            
            max_bit = max(bit_low, bit_med, bit_high)
            bit_label = ['low', 'medium', 'high'][[bit_low, bit_med, bit_high].index(max_bit)]
            print(f"      - Gorzkość: {bit_label} ({max_bit:.3f})")
            
            max_aci = max(aci_low, aci_med, aci_high)
            aci_label = ['low', 'medium', 'high'][[aci_low, aci_med, aci_high].index(max_aci)]
            print(f"      - Kwasowość: {aci_label} ({max_aci:.3f})")
            
            max_aro = max(aro_weak, aro_mod, aro_strong)
            aro_label = ['weak', 'moderate', 'strong'][[aro_weak, aro_mod, aro_strong].index(max_aro)]
            print(f"      - Aromat: {aro_label} ({max_aro:.3f})")
            
            max_temp = max(temp_low, temp_opt, temp_high)
            temp_label = ['low', 'optimal', 'high'][[temp_low, temp_opt, temp_high].index(max_temp)]
            print(f"      - Temperatura: {temp_label} ({max_temp:.3f})")
            
        except Exception as e:
            print(f"    ⚠️  Nie udało się wyświetlić szczegółów aktywacji: {e}")
    
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