# HospitalWasteManagement/src/indirect.py
import pint

# Initialize the Pint unit registry.
ureg = pint.UnitRegistry()

class IndirectEmissionsCalculator:
    """
    Calculates indirect emissions based on hospital-specific factors.
    
    This includes emissions from:
      - Energy inputs (e.g., electricity consumption)
      - Transportation (e.g., waste hauling)
      - Infrastructure (e.g., construction-related emissions, land occupation)
      - Downstream emissions (e.g., emissions from residues)
    
    The calculator uses a dictionary of factors, which should include sub-dictionaries
    for "energy_inputs", "transportation", "infrastructure", and "downstream". Each sub-dictionary 
    is expected to contain keys with numerical factors.
    
    Example structure of factors:
    
        {
            "energy_inputs": {
                "energy_use_kWh_per_kg": 0.12,
                "co2_fossil_per_kWh": 0.50,
                "so2_per_kWh": 0.00025,
                "pm25_per_kWh": 0.00012,
            },
            "transportation": {
                "distance_km": 0.5,
                "truck_load_t": 10 * 0.44,
                "co2_fossil_per_tkm": 0.09,
                "nox_per_tkm": 0.0012,
            },
            "infrastructure": {
                "construction_co2_per_kg": 0.02,
                "land_use_factor": 0.001,
            },
            "downstream": {
                "residue_ratio": 0.06 * 0.44,
                "residue_co2_per_kg": 0.20,
                "residue_so2_per_kg": 0.001,
            },
        }
    """
    def __init__(self, factors: dict):
        """
        Initializes the calculator with a dictionary of hospital-specific factors.
        
        Args:
            factors (dict): A dictionary containing the sub-dictionaries for each emission category.
        """
        self.factors = factors
    
    def calculate(self, waste) -> dict:
        """
        Calculates the indirect emissions for the given waste stream.
        
        Args:
            waste: An object that has a 'mass' attribute (a Pint quantity).
        
        Returns:
            dict: A dictionary mapping emission keys (e.g., "co2_fossil", "so2") to Pint quantities.
        """
        # Convert the waste mass to kilograms.
        mass = waste.mass.to("kg").magnitude
        
        # Retrieve sub-dictionaries for each emission category.
        energy = self.factors.get("energy_inputs", {})
        transport = self.factors.get("transportation", {})
        infra = self.factors.get("infrastructure", {})
        downstream = self.factors.get("downstream", {})
        
        emissions = {}
        
        # Calculate energy-related emissions.
        energy_use = mass * energy.get("energy_use_kWh_per_kg", 0)  # kWh used by the waste processing
        emissions["co2_fossil"] = energy_use * energy.get("co2_fossil_per_kWh", 0) * ureg("kg")
        emissions["so2"] = energy_use * energy.get("so2_per_kWh", 0) * ureg("kg")
        emissions["pm25"] = energy_use * energy.get("pm25_per_kWh", 0) * ureg("kg")
        
        # Calculate transportation emissions.
        waste_tonnes = mass / 1000.0  # Convert mass from kg to tonnes.
        distance = transport.get("distance_km", 0)
        tkm = waste_tonnes * distance  # tonne-kilometers.
        # Add transportation emissions to any pre-existing CO2 emissions.
        emissions["co2_fossil"] += tkm * transport.get("co2_fossil_per_tkm", 0) * ureg("kg")
        emissions["nox"] = tkm * transport.get("nox_per_tkm", 0) * ureg("kg")
        
        # Calculate infrastructure-related emissions.
        infra_co2 = mass * infra.get("construction_co2_per_kg", 0) * ureg("kg")
        emissions["co2_fossil"] += infra_co2
        emissions["land_occupation"] = mass * infra.get("land_use_factor", 0) * ureg("square_meter-year")
        
        # Calculate downstream emissions (e.g., residues).
        residue_mass = mass * downstream.get("residue_ratio", 0)
        residue_co2 = residue_mass * downstream.get("residue_co2_per_kg", 0) * ureg("kg")
        residue_so2 = residue_mass * downstream.get("residue_so2_per_kg", 0) * ureg("kg")
        emissions["co2_fossil"] += residue_co2
        emissions["so2"] += residue_so2
        
        return emissions