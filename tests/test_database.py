# HospitalWasteManagement/tests/test_database.py

import unittest
import logging
from pathlib import Path
from types import SimpleNamespace

import brightway2 as bw
import pint

from src.database import (
    setup_project,
    build_flow_index,
    retrieve_flows,
    create_or_reset_db,
    create_activity,
    add_production_exchange,
    add_biosphere_exchanges
)

# Initialize a Pint unit registry.
ureg = pint.UnitRegistry()

# Optional: Suppress excessive Brightway2 logging during tests.
logging.getLogger("brightway2").setLevel(logging.WARNING)


class TestDatabaseFunctions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """
        Set up a test project and create a test database to be used in the tests.
        """
        cls.test_project_name = "TestProjectForDatabaseTests"
        cls.bio_db = setup_project(cls.test_project_name)
        cls.flow_index = build_flow_index(cls.bio_db)
        cls.flows = retrieve_flows(cls.flow_index)
        cls.test_db_name = "TestDB"
        cls.test_db = create_or_reset_db(cls.test_db_name)

    def test_setup_project(self):
        """Test that the biosphere database is set up and returned."""
        self.assertIsNotNone(self.bio_db, "The biosphere database should not be None.")
        self.assertIn("biosphere3", bw.databases, "The biosphere database (biosphere3) should be available.")

    def test_build_and_retrieve_flows(self):
        """Test that building the flow index and retrieving flows returns a dictionary with expected keys."""
        self.assertIsInstance(self.flow_index, dict, "Flow index should be a dictionary.")
        self.assertIsInstance(self.flows, dict, "Retrieved flows should be a dictionary.")
        # Check that at least one expected key exists (e.g., 'co2_fossil').
        self.assertIn("co2_fossil", self.flows, "The 'co2_fossil' flow should be present in the retrieved flows.")

    def test_create_or_reset_db(self):
        """Test that a new database can be created or reset."""
        # After creating, the database name should be in bw.databases.
        self.assertIn(self.test_db_name, bw.databases, f"Database '{self.test_db_name}' should exist in Brightway2 databases.")

    def test_create_activity(self):
        """Test that an activity is created with the correct attributes."""
        code = "TEST_ACTIVITY"
        name = "Test Activity"
        unit = "kilogram"
        activity = create_activity(self.test_db, code, name, unit)
        self.assertEqual(activity["name"], name, "Activity name should match the provided name.")
        self.assertEqual(activity["unit"], unit, "Activity unit should be 'kilogram'.")

    def test_add_production_exchange(self):
        """Test that adding a production exchange creates exactly one production exchange for an activity."""
        code = "TEST_PROD_EX"
        name = "Test Production Exchange"
        activity = create_activity(self.test_db, code, name)
        # First, add a production exchange.
        add_production_exchange(activity, amount=1.0)
        # Count production exchanges.
        prod_exchanges = [exc for exc in list(activity.exchanges()) if exc["type"] == "production"]
        self.assertEqual(len(prod_exchanges), 1, "There should be exactly one production exchange after adding.")

        # If we add again, it should replace the existing one.
        add_production_exchange(activity, amount=1.0)
        prod_exchanges = [exc for exc in list(activity.exchanges()) if exc["type"] == "production"]
        self.assertEqual(len(prod_exchanges), 1, "There should still be exactly one production exchange after re-adding.")

    def test_add_biosphere_exchanges(self):
        """Test that biosphere exchanges are added to an activity based on an emissions dictionary and flows."""
        code = "TEST_BIOSPH_EX"
        name = "Test Biosphere Exchange"
        activity = create_activity(self.test_db, code, name)
        
        # Create a dummy emissions dictionary.
        emissions = {
            "co2_fossil": 10 * ureg("kg"),
            "so2": 5 * ureg("kg"),
            "pm25": 0 * ureg("kg")  # This one is negligible and should be skipped.
        }
        
        # Create a dummy flows dictionary. Each flow is a simple object with a 'key' attribute.
        dummy_flows = {
            "co2_fossil": SimpleNamespace(key="dummy_key_co2"),
            "so2": SimpleNamespace(key="dummy_key_so2"),
            "pm25": SimpleNamespace(key="dummy_key_pm25")
        }
        
        # Add biosphere exchanges.
        add_biosphere_exchanges(activity, emissions, dummy_flows)
        
        # Retrieve exchanges from the activity and count biosphere exchanges (skip production exchanges).
        biosphere_exchanges = [exc for exc in list(activity.exchanges()) if exc["type"] == "biosphere"]
        # In our emissions dictionary, only "co2_fossil" and "so2" should be added (pm25 is negligible).
        self.assertEqual(len(biosphere_exchanges), 2, "There should be two biosphere exchanges added to the activity.")
        
        # Optionally, verify that the exchanges have the correct units and input keys.
        for exc in biosphere_exchanges:
            self.assertTrue("kg" in str(exc["unit"]), "The unit of the exchange should include 'kg'.")
            self.assertTrue(exc["input"] in ["dummy_key_co2", "dummy_key_so2"],
                            "The exchange input key should match one of the dummy flow keys.")


if __name__ == '__main__':
    unittest.main()
