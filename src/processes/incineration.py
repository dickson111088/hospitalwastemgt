# HospitalWasteManagement/src/processes/incineration.py

import copy
import pint
from src.processes.base import TreatmentProcess

# Initialize the Pint unit registry.
ureg = pint.UnitRegistry()

class IncinerationProcess(TreatmentProcess):
    """
    Implements direct emission calculations for incineration.
    
    The calculation is based on the waste's organic composition. Two distinct portions
    of the organic fraction are considered: one corresponding to fossil-derived organics
    (e.g., needles and sharps plastic) and another for biogenic organics.
    
    Emission calculations:
      - CO2 emissions: Fossil-derived carbon is converted to CO2 using the factor (44/12),
        and similarly for biogenic carbon.
      - SO2 emissions: Calculated based on the total organic fraction and a conversion factor.
      - NOx, PM10, and PM25: Directly computed using the waste mass and emission factors.
      - Mercury (hg) and Lead (pb): Computed based on the metallic composition fractions.
    
    Scenario adjustments:
      If a scenario dictionary is provided and contains an "incineration_flue_gas_efficiency" key,
      the factors for PM10, PM25, and NOx are scaled to reflect improvements from flue-gas cleaning.
    """
    def calculate_direct_emissions(self, waste, scenario: dict = None) -> dict:
        # Work on a copy of the process factors so as not to modify the original configuration.
        f = copy.deepcopy(self.factors)
        
        # Apply scenario adjustments to account for flue gas cleaning efficiency.
        if scenario and "incineration_flue_gas_efficiency" in scenario:
            efficiency = scenario["incineration_flue_gas_efficiency"]
            f["pm10_per_organic"] *= (1 - efficiency)
            f["pm25_per_organic"] *= (1 - efficiency)
            f["nox_per_waste"] *= (1 - efficiency)
        
        # Retrieve the organic composition from the waste.
        comp = waste.composition["organic_materials"]
        total_organic = sum(comp.values())
        fossil_organic = comp.get("needles_sharps_plastic", 0)
        biogenic_organic = total_organic - fossil_organic
        
        # Convert waste mass to kilograms (assumed units).
        mass = waste.mass.to("kg").magnitude
        
        # Calculate emissions using the provided factors.
        emissions = {
            "co2_fossil": fossil_organic * mass * f["carbon_content_fossil"] * (44 / 12) * ureg("kg"),
            "co2_biogenic": biogenic_organic * mass * f["carbon_content_biogenic"] * (44 / 12) * ureg("kg"),
            "so2": total_organic * mass * f["so2_conversion"] * (64 / 32) * ureg("kg"),
            "nox": mass * f["nox_per_waste"] * ureg("kg"),
            "pm10": mass * total_organic * f["pm10_per_organic"] * ureg("kg"),
            "pm25": mass * total_organic * f["pm25_per_organic"] * ureg("kg"),
            "hg": mass * waste.composition["metallic_materials"].get("mercury_waste", 0) * f["hg_volatilization"] * ureg("kg"),
            "pb": mass * waste.composition["metallic_materials"].get("other_heavy_metals", 0) * f["pb_volatilization"] * ureg("kg"),
        }
        
        # If combustion efficiency is below a threshold (0.95), apply a penalty to PM emissions.
        if f.get("combustion_efficiency", 1.0) < 0.95:
            penalty = (0.95 - f["combustion_efficiency"]) * 2
            emissions["pm10"] *= (1 + penalty)
            emissions["pm25"] *= (1 + penalty)
        
        return emissions
