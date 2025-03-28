# HospitalWasteManagement/src/processes/landfill.py

import copy
import math
import pint
from src.processes.base import TreatmentProcess

# Initialize the Pint unit registry.
ureg = pint.UnitRegistry()

class LandfillProcess(TreatmentProcess):
    """
    Implements direct emission calculations for landfill treatment processes.

    This process models the emissions from landfill over a given time period,
    accounting for both fast and slow biodegradation of organic fractions.
    The model calculates emissions for biogenic methane (CH₄), biogenic carbon dioxide (CO₂),
    ammonia (NH₃), non-methane volatile organic compounds (NMVOC), and heavy metals (e.g., mercury and lead).

    The basic logic is as follows:
      - A fraction of the waste's organic matter biodegrades quickly (fast decay)
        while another fraction biodegrades slowly (slow decay).
      - Emission quantities are calculated using decay functions (1 - exp(-k * t))
        where k is the decay rate (fast or slow) and t is the time period.
      - Some factors (e.g., ch4_split, hg_factor) may be modified based on a scenario,
        such as the implementation of best landfill practices.
    """
    def calculate_direct_emissions(self, waste, scenario: dict = None) -> dict:
        # Create a copy of the emission factors to avoid modifying the original.
        f = copy.deepcopy(self.factors)
        
        # If the scenario indicates best practices for landfill, adjust the factors.
        if scenario and scenario.get("landfill_best_practices", False):
            f["ch4_split"] *= 0.8  # Reduce the methane split by 20%
            f["hg_factor"] *= 0.5  # Halve the mercury emission factor
        
        # Extract the time period and decay rates from the factors.
        t = f["time_period"]
        k_fast = f["fast_decay_rate"]
        k_slow = f["slow_decay_rate"]
        
        # Retrieve the organic waste fractions from the waste composition.
        comp_org = waste.composition["organic_materials"]
        # Assume that body_fluids and lab_cultures biodegrade faster.
        biodeg_frac = comp_org.get("body_fluids", 0) + comp_org.get("lab_cultures", 0)
        # Assume that needles/sharps plastic and pharmaceuticals are less biodegradable.
        slow_frac = comp_org.get("needles_sharps_plastic", 0) + comp_org.get("pharmaceuticals", 0)
        
        # Calculate the fraction of organics that have decayed over the time period.
        fast_decayed = 1 - math.exp(-k_fast * t)
        slow_decayed = 1 - math.exp(-k_slow * t)
        
        # Convert the waste mass to kilograms.
        mass = waste.mass.to("kg").magnitude
        
        # Calculate emissions for each pollutant.
        ch4_biogenic = mass * biodeg_frac * fast_decayed * f["ch4_split"]
        co2_biogenic = mass * (biodeg_frac * fast_decayed * f["co2_split"] +
                               slow_frac * slow_decayed * 0.1)
        nh3_emission = mass * biodeg_frac * fast_decayed * f["nh3_split"]
        nmvoc_emission = mass * (biodeg_frac * fast_decayed * f["nmvoc_split"] +
                                 slow_frac * slow_decayed * f["nmvoc_split"] * 0.5)
        
        emissions = {
            "ch4_biogenic": ch4_biogenic * ureg("kg"),
            "co2_biogenic": co2_biogenic * ureg("kg"),
            "hg": mass * waste.composition["metallic_materials"].get("mercury_waste", 0) * f["hg_factor"] * t * ureg("kg"),
            "pb": mass * waste.composition["metallic_materials"].get("other_heavy_metals", 0) * f["pb_factor"] * t * ureg("kg"),
            "nmvoc": nmvoc_emission * ureg("kg"),
            "nh3": nh3_emission * ureg("kg"),
        }
        
        return emissions
