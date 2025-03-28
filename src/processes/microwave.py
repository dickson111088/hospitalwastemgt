# HospitalWasteManagement/src/processes/microwave.py

import copy
import pint
from src.processes.base import TreatmentProcess

# Initialize the Pint unit registry.
ureg = pint.UnitRegistry()

class MicrowaveProcess(TreatmentProcess):
    """
    Implements direct emission calculations for the microwave treatment process.

    Microwave treatment uses high-frequency electromagnetic radiation to treat waste.
    The emissions profile is influenced by:
      - The organic fraction of the waste, with a special emphasis on plastic content.
      - The difference between a base frequency and the operating frequency, which affects
        the formation of certain emissions via a frequency multiplier.
      - Electricity consumption leading to indirect CO₂ emissions.
      - Metal aerosol formation from the metallic fraction of the waste.

    The following factors (supplied via self.factors) are used in the calculation:
      - nmvoc_per_organic, pm10_per_organic, pm25_per_organic: Emission factors per unit organic mass.
      - base_frequency, operating_frequency, freq_impact_per_mhz: For calculating a frequency multiplier.
      - plastic_nmvoc_boost: A boost factor applied to NMVOC emissions based on the fraction of plastic.
      - elec_per_waste, grid_co2_factor: For computing electricity-related CO₂ emissions.
      - metal_aerosol_factor: For calculating metal aerosol (e.g., lead) emissions.
      - emission_limits: A dictionary with limits for "nmvoc", "pm10", and "pm25" (expressed per unit mass of waste).
      - enforce_emission_limits: A boolean indicating whether the calculated emissions should be capped to these limits.
    """
    def calculate_direct_emissions(self, waste, scenario: dict = None) -> dict:
        # Work on a copy of the factors to avoid modifying the original.
        f = copy.deepcopy(self.factors)
        
        # Retrieve the organic composition.
        comp_org = waste.composition["organic_materials"]
        total_organic = sum(comp_org.values())
        
        # Calculate the plastic fraction within the organic materials.
        plastic_frac = (comp_org.get("needles_sharps_plastic", 0) / total_organic) if total_organic > 0 else 0
        
        # Compute the frequency multiplier based on the difference between the base and operating frequencies.
        freq_diff = f["base_frequency"] - f["operating_frequency"]
        freq_multiplier = 1 + max(freq_diff, 0) * f["freq_impact_per_mhz"]
        
        # Calculate the NMVOC boost due to plastic content.
        plastic_boost = 1 + plastic_frac * f["plastic_nmvoc_boost"]
        
        # Convert the waste mass to kilograms.
        mass = waste.mass.to("kg").magnitude
        
        # Calculate raw emissions:
        # NMVOC emissions are boosted by both the frequency multiplier and the plastic content.
        raw_nmvoc = mass * total_organic * f["nmvoc_per_organic"] * freq_multiplier * plastic_boost
        # PM10 and PM25 emissions are influenced by the frequency multiplier.
        raw_pm10 = mass * total_organic * f["pm10_per_organic"] * freq_multiplier
        raw_pm25 = mass * total_organic * f["pm25_per_organic"] * freq_multiplier
        # CO₂ emissions from electricity consumption.
        energy_co2 = mass * f["elec_per_waste"] * f["grid_co2_factor"]
        # Metal aerosol emissions from the metallic fraction (using "other_heavy_metals" for lead).
        metal_emissions = mass * waste.composition["metallic_materials"].get("other_heavy_metals", 0) * f["metal_aerosol_factor"]
        
        # Construct the emissions dictionary, attaching units via Pint.
        emissions = {
            "nmvoc": raw_nmvoc * ureg("kg"),
            "pm10": raw_pm10 * ureg("kg"),
            "pm25": raw_pm25 * ureg("kg"),
            "co2_fossil": energy_co2 * ureg("kg"),
            "pb": metal_emissions * ureg("kg"),
        }
        
        # Enforce emission limits if required.
        if f.get("enforce_emission_limits", False):
            for pollutant in ["nmvoc", "pm10", "pm25"]:
                limit = f["emission_limits"].get(pollutant)
                if limit is not None:
                    # Cap the emission for the pollutant at mass * limit.
                    if emissions[pollutant].magnitude > mass * limit:
                        emissions[pollutant] = mass * limit * ureg("kg")
        
        return emissions
