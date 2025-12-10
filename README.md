# BrewSense - Coffee Quality Assessment System

A fuzzy logic system for automatic coffee quality assessment based on four parameters: bitterness, acidity, aroma, and temperature.

## Project Description

**BrewSense** is an application that uses fuzzy logic to evaluate coffee quality. The system analyzes four key parameters and determines a quality score on a 0-100 scale with a textual description.

### Technologies Used:
- **Python 3.8+** - programming language
- **scikit-fuzzy** - fuzzy logic implementation
- **tkinter** - graphical user interface
- **matplotlib** - chart visualization
- **numpy** - numerical computations

## Features

### Input Parameters:
- **Bitterness** [0-10] - intensity of bitter taste
- **Acidity** [0-10] - acidity level
- **Aroma** [0-10] - aroma intensity
- **Temperature** [60-95°C] - beverage temperature

### Quality Assessment:
The system determines quality on a **0-100** scale with the following categories:
- **Very Poor** (0-30)
- **Poor** (30-50)
- **Average** (50-70)
- **Good** (70-85)
- **Very Good** (85-92)
- **Excellent!** (92-100)

### Graphical Interface:
- Interactive sliders for parameter adjustment
- Coffee cup visualization with fill proportional to quality
- Animated steam above cup (when temperature > 75°C)
- Membership function plots for all variables
- Defuzzification plot with marked result
- Colorful progress bar
- Dynamic coffee color change based on quality

## Requirements

### System Requirements:
- **Python 3.8** or newer
- **Operating System**: Windows, Linux, or macOS
- **RAM**: minimum 512 MB
- **Screen Resolution**: minimum 1400x900 px

### Python Libraries:
```
scikit-fuzzy==0.4.2
numpy>=1.24.0
matplotlib>=3.7.0
```

## Installation

### Step 1: Download the Project
```bash
# Clone the repository or download files to project folder
cd brewsense
```

### Step 2: Create Virtual Environment (Recommended)
```bash
# Create venv
python -m venv venv

# Activate virtual environment
# On Windows:
.\venv\Scripts\Activate.ps1

# On Linux/Mac:
source venv/bin/activate
```

### Step 3: Go to src directory
```bash
cd src/
```

### Step 4: Install Dependencies
```bash
pip install -r requirements.txt
```

### Additional Steps for Linux:
If you encounter issues with tkinter:
```bash
sudo apt-get install python3-tk
```

## Running the Application

After installing dependencies, run the application:

```bash
python main.py
```

Or directly through the interpreter:
```bash
python -m main
```

## Usage

### Basic Steps:

1. **Launch the application** - a window with three panels will appear

2. **Set coffee parameters** (left panel):
   - Move sliders for each parameter
   - Values update automatically

3. **Evaluate coffee**:
   - Click the **"Oceń Kawę"** (Evaluate Coffee) button
   - System will calculate quality and update visualizations

4. **Observe results**:
   - **Right panel**: Cup visualization with filling
   - **Middle panel**: Membership function plots
   - **Bottom panel**: Numerical and textual result

5. **Reset**:
   - Click **"Reset"** to return to default values

### Tips:
- **Aroma** is the most important parameter
- Balance of **bitterness** and **acidity** increases score
- **Optimal temperature** (around 80°C) gives better results
- Extreme values decrease quality

## Project Structure

```
brewsense/src
│
├── main.py              # Application entry point
├── fuzzy_system.py      # Fuzzy system implementation
├── gui.py               # Graphical user interface
├── requirements.txt     # Project dependencies
├── README.md           # Documentation (this file)
│
└── venv/               # Virtual environment (after creation)
```

### File Descriptions:

#### `main.py`
Simple application entry point. Imports and runs the GUI.

#### `fuzzy_system.py`
Contains the `CoffeeQualitySystem` class with:
- Fuzzy variable definitions (antecedent/consequent)
- Membership functions (trapezoidal, triangular)
- 25 inference rules
- `evaluate()` method for quality calculation
- Centroid defuzzification method

#### `gui.py`
Contains classes:
- `CoffeeGUI` - main application window
- `CoffeeVisualizer` - coffee cup drawing
- All widget and event handling
- Matplotlib integration

## Technical Details

### Fuzzy System

#### Input Variables:
Each variable has 3 membership functions:

**Bitterness, Acidity:**
- Low: trapezoid [0, 0, 2, 4]
- Medium: triangle [2, 5, 8]
- High: trapezoid [6, 8, 10, 10]

**Aroma:**
- Weak: trapezoid [0, 0, 2, 4]
- Moderate: triangle [3, 5, 7]
- Strong: trapezoid [6, 8, 10, 10]

**Temperature:**
- Low: trapezoid [60, 60, 70, 75]
- Optimal: triangle [72, 80, 88]
- High: trapezoid [85, 90, 95, 95]

#### Output Variable (Quality):
6 membership functions:
- Very Poor: trapezoid [0, 0, 15, 30]
- Poor: triangle [20, 35, 50]
- Average: triangle [40, 55, 70]
- Good: triangle [60, 75, 85]
- Very Good: triangle [75, 85, 95]
- Excellent: trapezoid [85, 92, 100, 100]

#### Rule Base:
25 **IF-THEN** rules combining input values to determine output quality.

**Example Rules:**
- IF Aroma=Strong AND Bitterness=Medium AND Acidity=Medium AND Temp=Optimal THEN Quality=Excellent
- IF Aroma=Weak AND Bitterness=High AND Acidity=High AND Temp=Optimal THEN Quality=Very_Poor

**Rule Design Principles:**
- Aroma is the most important parameter (strong aroma → higher score)
- Balance of bitterness and acidity is crucial (medium values = better)
- Optimal temperature increases score
- Extremes (very strong bitterness, no aroma) decrease quality

**Inference Method:** Mamdani  
**Defuzzification:** Centroid (center of gravity)

## Usage Examples

### Test Scenarios:

**Excellent Coffee:**
```
Bitterness: 5.0
Acidity: 5.0
Aroma: 9.0
Temperature: 80°C
Expected Result: ~90-95 (Excellent!)
```

**Average Coffee:**
```
Bitterness: 5.0
Acidity: 4.0
Aroma: 5.0
Temperature: 78°C
Expected Result: ~55-65 (Average)
```

**Poor Coffee:**
```
Bitterness: 8.5
Acidity: 2.0
Aroma: 3.0
Temperature: 68°C
Expected Result: ~25-35 (Poor)
```

## Troubleshooting

### Common Issues:

**Problem: "ModuleNotFoundError: No module named 'tkinter'"**
```bash
# Linux:
sudo apt-get install python3-tk

# macOS:
brew install python-tk
```

**Problem: "ModuleNotFoundError: No module named 'skfuzzy'"**
```bash
# Make sure virtual environment is activated
pip install -r requirements.txt
```

**Problem: Window doesn't display correctly**
- Check screen resolution (minimum 1400x900)
- Try adjusting system DPI scaling

**Problem: Slow performance**
- Close other applications
- Check if Python 3.8+ is installed
- Verify that matplotlib uses correct backend

## Notes

- All code comments are in **Polish** (as per project requirements)
- Variable names follow **English** naming conventions (Python PEP 8)
- GUI labels are in Polish for consistency with the original specification
- The system uses **Mamdani inference** with **centroid defuzzification**

## Development

### Code Style:
- Follows PEP 8 guidelines
- Comprehensive docstrings in Polish
- Modular architecture for easy maintenance

### Future Enhancements:
- [ ] Multi-language support for GUI
- [ ] Export results to PDF/CSV
- [ ] Custom rule editor
- [ ] Historical data tracking
- [ ] Machine learning integration for rule optimization

##  License

This project is developed for educational purposes as part of a Fuzzy Systems course.

## Acknowledgments

Built with:
- [scikit-fuzzy](https://github.com/scikit-fuzzy/scikit-fuzzy) - Fuzzy logic toolkit
- [matplotlib](https://matplotlib.org/) - Visualization library
- [NumPy](https://numpy.org/) - Numerical computing