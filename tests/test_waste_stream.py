# HospitalWasteManagement/tests/test_waste_stream.py

import unittest
import pint
from src.waste_stream import WasteStream
from src import config  # To compare against default configuration values

# Initialize the Pint unit registry.
ureg = pint.UnitRegistry()

class TestWasteStream(unittest.TestCase):
    def setUp(self):
        # Create a WasteStream instance with a mass of 100 kg.
        self.mass = 100 * ureg("kg")
        self.waste_stream = WasteStream(mass=self.mass)

    def test_adjust_for_segregation(self):
        """
        Test that the adjust_for_segregation method correctly scales hazardous fractions.
        For example, the 'needles_sharps_plastic' fraction in the organic materials should
        be multiplied by the provided efficiency factor.
        """
        efficiency = 0.5
        adjusted_ws = self.waste_stream.adjust_for_segregation(efficiency)
        
        # Retrieve the original and adjusted fraction for needles_sharps_plastic.
        original_value = self.waste_stream.composition["organic_materials"].get("needles_sharps_plastic", 0)
        adjusted_value = adjusted_ws.composition["organic_materials"].get("needles_sharps_plastic", 0)
        
        self.assertAlmostEqual(
            adjusted_value,
            original_value * efficiency,
            msg="The 'needles_sharps_plastic' fraction should be reduced by the efficiency factor."
        )

    def test_original_composition_unchanged(self):
        """
        Test that adjusting the waste stream for segregation does not modify the original composition.
        """
        efficiency = 0.3
        _ = self.waste_stream.adjust_for_segregation(efficiency)
        
        # The original value should remain equal to the default value from the configuration.
        expected_value = config.DEFAULT_COMPOSITION["organic_materials"]["needles_sharps_plastic"]
        original_value = self.waste_stream.composition["organic_materials"]["needles_sharps_plastic"]
        
        self.assertAlmostEqual(
            original_value,
            expected_value,
            msg="The original waste stream composition should remain unchanged after adjustment."
        )

if __name__ == '__main__':
    unittest.main()
