# Hospital Waste Management LCA

This project implements a Life Cycle Assessment (LCA) framework for hospital waste management using the Brightway2 framework. The model estimates the environmental impacts associated with different biomedical waste treatment technologies—including incineration, landfill, pyrolysis, chemical disinfection, autoclave, and microwave processes—by combining both direct and indirect emissions. Various scenarios (e.g., BASELINE, ENHANCED_INCINERATION, HIGH_TECH, etc.) are modeled to assess the influence of process improvements and policy interventions.

## Table of Contents

- [Introduction](#introduction)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Usage](#usage)
- [Testing](#testing)
- [Contributing](#contributing)
- [License](#license)
- [Notes](#Notes)

## Introduction

Hospital waste management is a critical environmental and public health issue. This project provides a modular, scalable LCA framework that:
- **Models multiple treatment technologies** with process-specific emission factors.
- **Accounts for both direct and indirect emissions** (e.g., energy use, transportation, infrastructure).
- **Integrates scenario analysis** to evaluate the effects of different waste segregation efficiencies, process improvements, and policy changes.
- **Uses Brightway2** for database management and LCIA calculations and **Pint** for unit handling.

## Project Structure

The project is organized as follows:

```
HospitalWasteManagement/
├── src/
│   ├── __init__.py
│   ├── config.py                # Project configuration and constants (emission factors, waste composition, scenarios, etc.)
│   ├── waste_stream.py          # Definition of the WasteStream class to represent waste flows.
│   ├── processes/               # Module containing treatment process implementations.
│   │   ├── __init__.py
│   │   ├── base.py              # Abstract base class for treatment processes.
│   │   ├── incineration.py      # Incineration process calculations.
│   │   ├── landfill.py          # Landfill process calculations.
│   │   ├── pyrolysis.py         # Pyrolysis process calculations.
│   │   ├── chem_disinfection.py # Chemical disinfection process calculations.
│   │   ├── autoclave.py         # Autoclave process calculations.
│   │   └── microwave.py         # Microwave process calculations.
│   ├── indirect.py              # Indirect emissions calculator based on hospital-specific factors.
│   ├── database.py              # Functions for setting up the Brightway2 project, managing databases, and handling flows.
│   ├── lcia.py                 # Functions for calculating LCIA scores.
│   └── main.py                  # Main execution script tying all components together.
├── tests/
│   ├── __init__.py
│   ├── test_waste_stream.py   # Unit tests for the WasteStream class.
│   ├── test_processes.py      # Unit tests for treatment process calculations.
│   └── test_database.py       # Unit tests for database and biosphere flow functions.
├── requirements.txt           # Python dependencies (e.g., brightway2, pint)
└── README.md                  # This file.
```

## Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/dickson111088/hospitalwastemgt
   cd HospitalWasteManagement
   ```

2. **Create and Activate a Virtual Environment**

   ```bash
   python -m venv venv
   source venv/bin/activate    # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

   The `requirements.txt` file includes dependencies such as:
   - `brightway2`
   - `pint`

## Usage

To run the LCA model and generate scenario results, execute:

```bash
python src/main.py
```

This script will:
- Set up the Brightway2 project and load the biosphere database.
- Create a process database for hospital waste management activities.
- Generate waste streams for each hospital and adjust them based on segregation efficiency.
- Calculate direct emissions for each treatment process and add indirect emissions (if applicable).
- Compute LCIA scores for various impact categories.
- Export the results to a CSV file (`scenario_results.csv`).

## Testing

Unit tests are provided to validate the functionality of key modules. To run the tests, execute:

```bash
python -m unittest discover tests
```

## Contributing

Contributions are welcome! If you have suggestions, bug fixes, or improvements, please open an issue or submit a pull request.

## License

This project is licensed under the MIT License.
Feel free to modify the content of the README to suit your project's needs. This file provides an overview of the project, explains its structure, details installation and usage instructions, and outlines how to run tests and contribute.


## Notes

**src/**: Source code for the project.
**config.py**: External configurations and constants.
Explanation
Emission Factors:
The EMISSION_FACTORS dictionary holds the hard-coded values for each treatment process (incineration, landfill, and pyrolysis in this example).

Default Waste Composition:
DEFAULT_COMPOSITION defines the fractions for different waste material groups. These values are later used to model how much of each component is present in the waste stream.

Hospital-Specific Indirect Factors:
The HOSPITAL_INDIRECT_FACTORS dictionary contains separate configurations for KBTH, KATH, CCTH, BRH, and UCCH. Each hospital has its own sub-dictionary for energy inputs, transportation, infrastructure, and downstream emissions.

Impact Categories & Normalization Factors:
The impact categories dictionary (IMPACT_CATEGORIES) and normalization factors (NORMALIZATION_FACTORS) include eight categories that can be used in the LCIA step.

**waste_stream.py**: The `WasteStream` class and related functions.
  Explanation
Imports & Unit Registry:
We import necessary modules and create a Pint unit registry so that all numerical values can carry proper units (e.g., kilograms).

Dataclass Definition:
The WasteStream class is defined as a dataclass. It holds a mass (a Pint Quantity) and a composition dictionary. The default composition is obtained from config.DEFAULT_COMPOSITION.

adjust_for_segregation Method:
This method makes a deep copy of the current composition and scales down selected hazardous fractions (e.g., "needles_sharps_plastic", "cytotoxic_organic", and "lab_reagents") according to the provided segregation efficiency. The method then returns a new WasteStream instance with the adjusted composition.

**processes/**: Contains treatment process classes.
**base.py**: Base class for treatment processes.
    Explanation
Imports:
We import the ABC and abstractmethod from the abc module to define an abstract base class. The typing module is used for type hints, and pint is used for unit handling.

Unit Registry:
A Pint unit registry (ureg) is initialized to ensure that all numerical emissions values can be expressed with appropriate units.

TreatmentProcess Class:
This abstract base class defines the interface for all treatment processes. Each subclass (for example, incineration, landfill, pyrolysis, etc.) must implement the calculate_direct_emissions method, which takes a waste stream and an optional scenario and returns a dictionary of emissions as Pint quantities.


**incineration.py**: Incineration process class.
Explanation
Imports and Setup:
The file imports copy to safely work with a duplicate of the emission factors, pint for unit management, and the abstract base class TreatmentProcess from src/processes/base.py.

Unit Registry:
A Pint unit registry (ureg) is created so that all emissions quantities are attached to their respective units.

Class Definition:
IncinerationProcess extends the TreatmentProcess abstract class. It implements the calculate_direct_emissions method.

Scenario Adjustments:
The code checks if a scenario parameter (e.g., flue gas efficiency) is provided. If so, the emission factors for PM10, PM25, and NOx are scaled down to represent improved process performance.

Emission Calculations:
The waste's organic materials are separated into fossil-derived and biogenic fractions. These are then used to calculate CO₂, SO₂, NOx, PM10, and PM25 emissions using given factors. Emissions of mercury (hg) and lead (pb) are calculated using the waste's metallic composition.

Penalty Application:
If the combustion efficiency is below 0.95, a penalty multiplier is applied to the PM emissions, representing reduced performance in pollutant capture.

**landfill.py**: Landfill process class.
Explanation
Imports and Unit Registry:
The file imports required modules including copy, math, and pint, and it imports the abstract base class TreatmentProcess from src/processes/base.py. A Pint unit registry (ureg) is created to ensure that all emission values include appropriate units.

Class Definition:
The LandfillProcess class inherits from TreatmentProcess and implements the calculate_direct_emissions method. This method:

Creates a copy of the process factors.
Optionally adjusts certain factors (like ch4_split and hg_factor) if the scenario specifies best practices.
Extracts the time period and biodegradation decay rates (fast and slow).
Retrieves relevant fractions from the waste composition, differentiating between fractions that biodegrade quickly and those that do not.
Uses exponential decay functions (1 − exp(−k * t)) to model the fraction of waste that decays over the time period.
Computes emissions for various pollutants (CH₄, CO₂, NH₃, NMVOC) and heavy metals, applying the appropriate factors and converting results into Pint quantities.
Return Value:
The method returns a dictionary where keys represent pollutant names (e.g., "ch4_biogenic", "co2_biogenic", "hg", "pb", "nmvoc", "nh3") and values are the corresponding emission amounts as Pint quantities with units.

**pyrolysis.py**: Pyrolysis process class.
Explanation
Imports and Unit Registry:

The module imports the abstract base class TreatmentProcess from src/processes/base.py and the pint package for unit handling.
A Pint unit registry (ureg) is initialized to attach physical units (e.g., kilograms) to emission values.
PyrolysisProcess Class:

The PyrolysisProcess class inherits from the TreatmentProcess abstract class.
It implements the calculate_direct_emissions method, which computes direct emissions for a pyrolysis process.
Emission Calculations:

The code retrieves the organic and chlorinated waste compositions from the provided waste object.
The total organic fraction is calculated by summing the values in the "organic_materials" dictionary, and similarly for the chlorinated fraction.
The waste mass is converted to kilograms.
Emissions for CO₂ (fossil), CH₄ (fossil), NMVOC, PAHs, and dioxin are computed by multiplying the mass, the relevant fraction (total organic or total chlorinated), and the corresponding emission factor.
Emissions for mercury (hg) and lead (pb) are calculated based on their presence in the metallic fraction.
All emission amounts are multiplied by the appropriate units using the Pint registry.
Return Value:

The method returns a dictionary where each key (e.g., "co2_fossil", "dioxin") maps to a Pint quantity representing the calculated emissions.

**Autoclave**:
Explanation
Imports and Setup:
The file imports pint for unit management and the TreatmentProcess base class from src/processes/base.py. A Pint unit registry (ureg) is created for consistent unit handling.

AutoclaveProcess Class:
The AutoclaveProcess class inherits from TreatmentProcess and implements the calculate_direct_emissions method.

Emission Calculation Details:

Organic Fraction: The method calculates the total organic fraction from the waste’s composition.
Temperature Factor: It computes a temperature-driven NMVOC factor using the difference between operating_temp and baseline_temp and scales it with nmvoc_temp_coeff, ensuring the factor is at least 1.
Energy-Based CO₂ Emissions: The CO₂ emissions due to electricity usage are calculated using the waste mass, the electricity usage per unit waste, and the grid CO₂ factor.
Direct Emissions: NMVOC, PM10, and PM25 emissions are computed by multiplying the mass, the organic fraction, and the respective emission factors. Mercury emissions are calculated using the mercury fraction from the metallic materials and a leaching factor.
Return Value:
The method returns a dictionary where each key (e.g., "nmvoc", "co2_fossil") maps to a Pint quantity representing the calculated emissions.

**Microwave**:
Explanation
Imports and Initialization:

The module imports copy (to safely duplicate factors), pint (for unit management), and the abstract base class TreatmentProcess from src/processes/base.py.
A Pint unit registry (ureg) is instantiated so that all emission values are associated with proper units.
Class Definition (MicrowaveProcess):

This class inherits from TreatmentProcess and implements the calculate_direct_emissions method.
The method uses the microwave process emission factors provided in self.factors.
Emission Calculations:

Organic Fraction and Plastic Content:
The total organic fraction is computed from the waste composition. The plastic fraction is derived from the proportion of "needles_sharps_plastic" in the organic materials.
Frequency Multiplier:
A frequency multiplier is calculated using the difference between the base frequency and operating frequency (multiplied by a per-megahertz impact factor). This multiplier increases emissions when the operating frequency is sufficiently below the base frequency.
Plastic Boost:
NMVOC emissions are further boosted based on the fraction of plastic present.
Raw Emissions:
Raw NMVOC, PM10, PM25, and electricity-related CO₂ emissions are calculated by multiplying the waste mass, the total organic fraction, and the corresponding emission factors. Metal emissions (for lead, designated as "pb") are calculated from the metallic fraction.
Emission Limits:
If the enforce_emission_limits flag is enabled, the code checks whether the computed emissions for NMVOC, PM10, and PM25 exceed the specified limits (expressed per unit mass) and caps them if necessary.
Return Value:
The method returns a dictionary where each key (such as "nmvoc", "pm10", "co2_fossil", "pb") maps to a Pint quantity representing the calculated emissions.

**Chemical Disinfection**:
Explanation
Imports and Unit Registry:
The module imports copy (to work with a duplicate of the factors), pint (for unit management), and the base class TreatmentProcess from src/processes/base.py. A Pint unit registry (ureg) is initialized so that all emissions are attached to proper physical units.

Class Definition (ChemDisinfectionProcess):
The class inherits from TreatmentProcess and implements the calculate_direct_emissions method. This method calculates the direct emissions for a chemical disinfection process.

Calculation Details:

Chemical Disinfection Fraction:
The method first retrieves a chemical_disinfection_fraction from the scenario (if provided) and applies it to scale the treatable organic mass.
Total Organic Mass:
The total treatable organic mass is computed as the sum of the organic fractions multiplied by the waste mass and the disinfection fraction.
Disinfectant Used and Chlorine Emissions:
The disinfectant usage is calculated from the treatable organic mass and a predefined disinfectant ratio. Chlorine emissions (here represented as chlorine_air) are then computed based on the disinfectant usage, chlorine loss factor, and the fraction of chlorine converted to HCl.
NH3 Emissions:
The method computes the nitrogen content from the organic mass and converts it to NH3 using a conversion factor.
NMVOC and PM10 Emissions:
These are computed by multiplying the total organic mass by their respective emission factors.
Return Value:
The method returns a dictionary mapping pollutant keys ("chlorine_air", "nmvoc", "nh3", and "pm10") to their computed emission amounts, each attached to the unit "kg" using Pint.

**indirect.py**: Indirect emissions calculator.
  Explanation
Imports and Unit Registry:
The module imports pint and initializes a unit registry (ureg), ensuring that all numerical values carry proper physical units.

Class Documentation:
The IndirectEmissionsCalculator class is documented with an explanation of the expected structure for the factors dictionary. This dictionary includes sub-dictionaries for energy inputs, transportation, infrastructure, and downstream emissions.

Initialization:
The __init__ method takes a dictionary of factors and stores it.

Calculate Method:
The calculate method:
Converts the waste mass to kilograms.
Retrieves the relevant factors from the provided dictionary.
Computes energy-related emissions (CO₂, SO₂, PM₂.₅) based on the waste mass and energy use.
Computes transportation emissions based on the tonne-kilometers traveled.
Computes infrastructure emissions (CO₂ and land occupation).
Computes downstream emissions from waste residues.
Sums up contributions (for example, additional CO₂ from transportation and downstream emissions is added to the energy-related CO₂).

**database.py**: Functions for Brightway2 project and database management.
  Explanation
Project and Biosphere Setup:
The setup_project function creates (or sets) the project and ensures the biosphere3 database is loaded via bw2setup().

Flow Index Functions:
build_flow_index iterates over all flows in the biosphere database and builds an index (using each flow’s unique code).
get_flow_by_uuid retrieves an individual flow using its UUID, raising an error if not found.
retrieve_flows uses a predefined dictionary of UUIDs to create a mapping from short names (like "co2_fossil") to flow objects.

Database Creation and Activity Functions:
create_or_reset_db deletes and re-registers a database if it already exists.
create_activity creates a new activity in the database with the provided code, name, and unit.
add_production_exchange ensures the activity has a production exchange, removing any pre-existing ones.

Biosphere Exchanges:
add_biosphere_exchanges iterates over the calculated emissions and, if a corresponding flow exists and the emission is significant, creates a biosphere exchange in the activity.

**lcia.py**: LCIA calculation routines.
Explanation
Imports:

The module imports Python's built-in logging module to log any errors during LCIA computation.
It also imports brightway2 as bw, which is the LCA framework used in the project.
Function compute_lcia:

This function accepts a Brightway2 activity (which represents a treatment process in our case) and an LCIA method tuple.
It creates an LCA object using the provided activity (with a functional unit of 1) and the specified method.
It then performs the inventory analysis (lci()) and impact assessment (lcia()) steps.
Finally, it returns the LCIA score.
If any error occurs during these steps, the function logs an error message and returns 0.0.

**main.py**: Main execution script.
Explanation
Imports and Setup:
The script imports required modules (e.g., logging, csv, pathlib’s Path, brightway2, pint) and then imports project-specific modules from src (configuration, waste stream definition, treatment process classes, indirect emissions, database helper functions, and LCIA functions). A Pint unit registry is instantiated for unit handling.

Project Setup:
The setup_project function creates or sets the Brightway2 project and loads the biosphere database. Flows are then indexed and retrieved for later use in biosphere exchanges.

Database Creation:
The process database (for hospital activities) is created or reset.

Hospital and Scenario Definitions:
Hospitals (with their waste masses in kg) and scenarios (with parameters such as segregation efficiency, flue gas efficiency, and landfill best practices) are defined.

Process Initialization:
Six treatment processes (incineration, landfill, pyrolysis, chemical disinfection, autoclave, and microwave) are instantiated using emission factors from the configuration.

Processing Loop:
For each scenario and hospital, a WasteStream is created and adjusted based on the scenario’s segregation efficiency. If hospital-specific indirect factors are available, an IndirectEmissionsCalculator is instantiated. For each process, a new Brightway2 activity is created; direct emissions are calculated using the process model, indirect emissions (if any) are added, and then biosphere exchanges are recorded in the activity. LCIA scores are computed for each impact category (using methods and normalization factors from the configuration).

Results Export:
The results—raw and normalized LCIA scores for each hospital, process, and scenario—are written to a CSV file (scenario_results.csv).

Script Execution:
The main() function is invoked when the script is executed directly.

This main.py file integrates all components of the Hospital Waste Management LCA framework into a single workflow, from data input to LCIA output and result export.
