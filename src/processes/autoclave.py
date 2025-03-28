# HospitalWasteManagement/src/processes/autoclave.py

import pint
from src.processes.base import TreatmentProcess

# Initialize the Pint unit registry.
ureg = pint.UnitRegistry()

class AutoclaveProcess(TreatmentProcess):
    """
    Implements direct emission calculations for the autoclave treatment process.

    Autoclaving is a steam sterilization method used to treat waste, which primarily
    consumes electricity. Its emissions profile includes indirect emissions from grid
    electricity usage (resulting in CO₂ emissions) as well as minor direct emissions
    (such as NMVOC and particulate matter) related to the organic fraction in the waste.
    
    The calculation uses the following steps:
      1. Determine the total organic fraction of the waste from its composition.
      2. Calculate a temperature-driven NMVOC factor based on the difference between the
         operating temperature and a baseline temperature.
      3. Compute CO₂ emissions based on electricity consumption per unit waste and the grid CO₂ factor.
      4. Compute direct NMVOC, PM10, and PM25 emissions using the organic fraction.
      5. Calculate mercury (hg) emissions based on the fraction of mercury present in the metallic materials.
    
    The emission factors for autoclave are expected to be provided in the factors dictionary,
    for example:
    
        {
            "nmvoc_per_organic": 1e-5,
            "pm10_per_organic": 5e-5,
            "pm25_per_organic": 3e-5,
            "elec_per_waste": 0.6,
            "grid_co2_factor": 0.4,
            "baseline_temp": 121,
            "operating_temp": 134,
            "nmvoc_temp_coeff": 0.2,
            "hg_leach_factor": 0.001
        }
    """
    def calculate_direct_emissions(self, waste, scenario: dict = None) -> dict:
        # Use the provided autoclave factors.
        f = self.factors

        # Retrieve the organic fraction from the waste composition.
        comp_org = waste.composition["organic_materials"]
        total_organic = sum(comp_org.values())

        # Calculate the temperature difference factor for NMVOC emissions.
        temp_diff = f["operating_temp"] - f["baseline_temp"]
        nmvoc_factor = 1 + (temp_diff / 10) * f["nmvoc_temp_coeff"]
        nmvoc_factor = max(nmvoc_factor, 1.0)  # Ensure at least a factor of 1.

        # Convert waste mass to kilograms.
        mass = waste.mass.to("kg").magnitude

        # Calculate CO2 emissions from grid electricity usage.
        energy_co2 = mass * f["elec_per_waste"] * f["grid_co2_factor"]

        # Compute the emissions for each pollutant.
        emissions = {
            "nmvoc": mass * total_organic * f["nmvoc_per_organic"] * nmvoc_factor * ureg("kg"),
            "pm10": mass * total_organic * f["pm10_per_organic"] * ureg("kg"),
            "pm25": mass * total_organic * f["pm25_per_organic"] * ureg("kg"),
            "co2_fossil": energy_co2 * ureg("kg"),
            "hg": mass * waste.composition["metallic_materials"].get("mercury_waste", 0) * f["hg_leach_factor"] * ureg("kg"),
        }
        
        return emissions
