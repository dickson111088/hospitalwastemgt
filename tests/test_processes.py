# HospitalWasteManagement/tests/test_processes.py

import unittest
import pint
from src.waste_stream import WasteStream
from src.processes.incineration import IncinerationProcess
from src.processes.landfill import LandfillProcess
from src.processes.pyrolysis import PyrolysisProcess
from src.processes.chem_disinfection import ChemDisinfectionProcess
from src.processes.autoclave import AutoclaveProcess
from src.processes.microwave import MicrowaveProcess
from src import config

# Initialize the Pint unit registry.
ureg = pint.UnitRegistry()

class TestProcesses(unittest.TestCase):
    def setUp(self):
        # Create a dummy waste stream with a mass of 100 kg.
        self.mass = 100 * ureg("kg")
        self.waste_stream = WasteStream(mass=self.mass)
        # Define a common scenario dictionary for testing purposes.
        self.scenario = {
            "segregation_efficiency": 0.8,
            "incineration_flue_gas_efficiency": 0.5,
            "landfill_best_practices": True,
            "chemical_disinfection_fraction": 0.5
        }

    def test_incineration_process(self):
        proc = IncinerationProcess("Incineration", config.EMISSION_FACTORS["INCINERATION"])
        emissions = proc.calculate_direct_emissions(self.waste_stream, scenario=self.scenario)
        expected_keys = ["co2_fossil", "co2_biogenic", "so2", "nox", "pm10", "pm25", "hg", "pb"]
        for key in expected_keys:
            self.assertIn(key, emissions, f"Incineration emissions should include '{key}'.")
            self.assertTrue(hasattr(emissions[key], "units"), f"Emission '{key}' should have units.")

    def test_landfill_process(self):
        proc = LandfillProcess("Landfill", config.EMISSION_FACTORS["LANDFILL"])
        emissions = proc.calculate_direct_emissions(self.waste_stream, scenario=self.scenario)
        expected_keys = ["ch4_biogenic", "co2_biogenic", "hg", "pb", "nmvoc", "nh3"]
        for key in expected_keys:
            self.assertIn(key, emissions, f"Landfill emissions should include '{key}'.")
            self.assertTrue(hasattr(emissions[key], "units"), f"Emission '{key}' should have units.")

    def test_pyrolysis_process(self):
        proc = PyrolysisProcess("Pyrolysis", config.EMISSION_FACTORS["PYROLYSIS"])
        emissions = proc.calculate_direct_emissions(self.waste_stream, scenario=self.scenario)
        expected_keys = ["co2_fossil", "ch4_fossil", "nmvoc", "pahs", "dioxin", "hg", "pb"]
        for key in expected_keys:
            self.assertIn(key, emissions, f"Pyrolysis emissions should include '{key}'.")
            self.assertTrue(hasattr(emissions[key], "units"), f"Emission '{key}' should have units.")

    def test_chem_disinfection_process(self):
        # Use dummy emission factors if CHEM_DISINFECTION factors are not defined in config.
        chem_factors = config.EMISSION_FACTORS.get("CHEM_DISINFECTION", {
            "disinfectant_ratio": 0.1,
            "chlorine_loss": 0.05,
            "chlorine_to_hcl_split": 0.6,
            "nitrogen_content": 0.03,
            "nitrogen_to_nh3": 0.2,
            "nmvoc_per_organic": 1e-15,
            "pm10_per_organic": 2e-7
        })
        proc = ChemDisinfectionProcess("Chemical Disinfection", chem_factors)
        emissions = proc.calculate_direct_emissions(self.waste_stream, scenario=self.scenario)
        expected_keys = ["chlorine_air", "nmvoc", "nh3", "pm10"]
        for key in expected_keys:
            self.assertIn(key, emissions, f"Chemical Disinfection emissions should include '{key}'.")
            self.assertTrue(hasattr(emissions[key], "units"), f"Emission '{key}' should have units.")

    def test_autoclave_process(self):
        # Use dummy factors for Autoclave if not defined in config.
        auto_factors = config.EMISSION_FACTORS.get("AUTOCLAVE", {
            "nmvoc_per_organic": 1e-5,
            "pm10_per_organic": 5e-5,
            "pm25_per_organic": 3e-5,
            "elec_per_waste": 0.6,
            "grid_co2_factor": 0.4,
            "baseline_temp": 121,
            "operating_temp": 134,
            "nmvoc_temp_coeff": 0.2,
            "hg_leach_factor": 0.001
        })
        proc = AutoclaveProcess("Autoclave", auto_factors)
        emissions = proc.calculate_direct_emissions(self.waste_stream, scenario=self.scenario)
        expected_keys = ["nmvoc", "pm10", "pm25", "co2_fossil", "hg"]
        for key in expected_keys:
            self.assertIn(key, emissions, f"Autoclave emissions should include '{key}'.")
            self.assertTrue(hasattr(emissions[key], "units"), f"Emission '{key}' should have units.")

    def test_microwave_process(self):
        # Use dummy factors for Microwave if not defined in config.
        micro_factors = config.EMISSION_FACTORS.get("MICROWAVE", {
            "nmvoc_per_organic": 0.002,
            "pm10_per_organic": 0.0006,
            "pm25_per_organic": 0.0004,
            "base_frequency": 2450,
            "operating_frequency": 915,
            "freq_impact_per_mhz": 0.0002,
            "plastic_nmvoc_boost": 0.8,
            "elec_per_waste": 0.7,
            "grid_co2_factor": 0.4,
            "metal_aerosol_factor": 0.005,
            "emission_limits": {
                "nmvoc": 0.003,
                "pm10": 0.002,
                "pm25": 0.001,
            },
            "enforce_emission_limits": True
        })
        proc = MicrowaveProcess("Microwave", micro_factors)
        emissions = proc.calculate_direct_emissions(self.waste_stream, scenario=self.scenario)
        expected_keys = ["nmvoc", "pm10", "pm25", "co2_fossil", "pb"]
        for key in expected_keys:
            self.assertIn(key, emissions, f"Microwave emissions should include '{key}'.")
            self.assertTrue(hasattr(emissions[key], "units"), f"Emission '{key}' should have units.")

if __name__ == '__main__':
    unittest.main()
