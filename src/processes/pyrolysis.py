# HospitalWasteManagement/src/processes/pyrolysis.py

from src.processes.base import TreatmentProcess
import pint

# Initialize the Pint unit registry.
ureg = pint.UnitRegistry()

class PyrolysisProcess(TreatmentProcess):
    """
    Implements direct emission calculations for the pyrolysis treatment process.
    
    Pyrolysis is a thermal treatment method that decomposes waste material in the absence of oxygen.
    This process converts organic and chlorinated fractions of the waste into various emissions.
    
    Emission calculations:
      - Fossil CO2: Calculated using the total organic fraction and the emission factor 'co2_fossil_per_organic'.
      - Fossil CH4: Calculated using the total organic fraction and the emission factor 'ch4_fossil_per_organic'.
      - NMVOC: Calculated using the total organic fraction and the emission factor 'nmvoc_per_organic'.
      - PAHs: Calculated using the total organic fraction and the emission factor 'pahs_per_organic'.
      - Dioxin: Calculated using the total chlorinated material and the emission factor 'dioxin_per_chlorinated'.
      - Mercury (hg) and Lead (pb): Calculated based on the respective fractions in the metallic materials.
    
    Note:
      - The method accepts an optional `scenario` dictionary. In this basic implementation, scenario
        parameters are not used to modify the factors, but the parameter is available for future extensions.
    """
    def calculate_direct_emissions(self, waste, scenario: dict = None) -> dict:
        # Use the emission factors provided for pyrolysis.
        f = self.factors
        
        # Retrieve organic and chlorinated compositions from the waste.
        comp_org = waste.composition["organic_materials"]
        comp_chlor = waste.composition["chlorinated_materials"]
        
        # Calculate total organic and total chlorinated fractions.
        total_organic = sum(comp_org.values())
        total_chlor = sum(comp_chlor.values())
        
        # Convert waste mass to kilograms.
        mass = waste.mass.to("kg").magnitude
        
        # Calculate emissions for each pollutant.
        emissions = {
            "co2_fossil": mass * total_organic * f["co2_fossil_per_organic"] * ureg("kg"),
            "ch4_fossil": mass * total_organic * f["ch4_fossil_per_organic"] * ureg("kg"),
            "nmvoc": mass * total_organic * f["nmvoc_per_organic"] * ureg("kg"),
            "pahs": mass * total_organic * f["pahs_per_organic"] * ureg("kg"),
            "dioxin": mass * total_chlor * f["dioxin_per_chlorinated"] * ureg("kg"),
            "hg": mass * waste.composition["metallic_materials"].get("mercury_waste", 0) * f["hg_per_mercury"] * ureg("kg"),
            "pb": mass * waste.composition["metallic_materials"].get("other_heavy_metals", 0) * f["pb_per_heavy_metal"] * ureg("kg"),
        }
        
        return emissions
