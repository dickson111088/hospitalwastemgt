# HospitalWasteManagement/src/processes/chem_disinfection.py

import copy
import pint
from src.processes.base import TreatmentProcess

# Initialize the Pint unit registry.
ureg = pint.UnitRegistry()

class ChemDisinfectionProcess(TreatmentProcess):
    """
    Implements direct emission calculations for the chemical disinfection treatment process.

    Chemical disinfection uses chemical agents (e.g., chlorine-based compounds) to disinfect waste.
    This process may lead to emissions such as:
      - Chlorine emissions to air (represented here as 'chlorine_air'),
      - NMVOC (non-methane volatile organic compounds),
      - Ammonia (NH3) produced from nitrogen in the waste, and
      - Particulate matter (PM10).

    The calculation steps are:
      1. Determine a chemical disinfection fraction (from a scenario) that scales the treatable organic mass.
      2. Compute the total treatable organic mass as the sum of the organic fractions multiplied by the waste mass.
      3. Calculate the amount of disinfectant used as the product of the total organic mass and a disinfectant ratio.
      4. Compute chlorine emissions as:
             disinfectant_used * chlorine_loss * (1 - chlorine_to_hcl_split)
      5. Compute the nitrogen content from the total organic mass and convert it to NH3 using a conversion factor.
      6. Compute NMVOC and PM10 emissions as the product of the total organic mass and their respective emission factors.
    
    All computed emission values are returned as Pint quantities.
    """
    def calculate_direct_emissions(self, waste, scenario: dict = None) -> dict:
        # Work on a copy of the emission factors to avoid modifying the original.
        f = copy.deepcopy(self.factors)
        
        # Retrieve the chemical disinfection fraction from the scenario, defaulting to 1.0 if not provided.
        chem_fraction = scenario.get("chemical_disinfection_fraction", 1.0) if scenario else 1.0
        
        # Retrieve the organic waste composition.
        comp_org = waste.composition["organic_materials"]
        org_sum = sum(comp_org.values())
        
        # Convert waste mass to kilograms.
        mass = waste.mass.to("kg").magnitude
        
        # Calculate the total treatable organic mass (in kg).
        total_organic = org_sum * mass * chem_fraction
        
        # Compute the amount of disinfectant used (assumed to be proportional to the treatable organic mass).
        disinfectant_used = total_organic * f["disinfectant_ratio"]
        
        # Calculate chlorine emissions (to air) from the loss of chlorine in the disinfectant.
        cl2_emission = disinfectant_used * f["chlorine_loss"] * (1 - f["chlorine_to_hcl_split"])
        
        # Calculate nitrogen-based emissions: determine the nitrogen content and convert it to NH3.
        nitrogen_content = total_organic * f["nitrogen_content"]
        nh3_emission = nitrogen_content * f["nitrogen_to_nh3"]
        
        # Calculate emissions for NMVOC and PM10 based on the treatable organic mass.
        nmvoc_emission = total_organic * f["nmvoc_per_organic"]
        pm10_emission = total_organic * f["pm10_per_organic"]
        
        # Construct the emissions dictionary (with units attached via Pint).
        emissions = {
            "chlorine_air": cl2_emission * ureg("kg"),
            "nmvoc": nmvoc_emission * ureg("kg"),
            "nh3": nh3_emission * ureg("kg"),
            "pm10": pm10_emission * ureg("kg"),
        }
        
        return emissions
