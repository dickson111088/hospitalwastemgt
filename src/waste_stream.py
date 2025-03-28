# src/waste_stream.py
import copy
from dataclasses import dataclass, field
from typing import Dict
import pint
from src import config

# Set up a Pint unit registry.
ureg = pint.UnitRegistry()

@dataclass
class WasteStream:
    """
    Represents a waste stream with a given mass (with unit) and a material composition.

    Attributes:
        mass (pint.Quantity): The total mass of the waste stream. For example, 100 * ureg("kg").
        composition (Dict[str, Dict[str, float]]): A nested dictionary that defines the fraction of
            each material group present in the waste. The structure is typically:
                {
                    "organic_materials": { ... },
                    "chlorinated_materials": { ... },
                    "metallic_materials": { ... },
                    "radioactive_materials": { ... }
                }
            The default composition is loaded from the config module.
    """
    mass: pint.Quantity  # e.g., 100 * ureg("kg")
    composition: Dict[str, Dict[str, float]] = field(
        default_factory=lambda: copy.deepcopy(config.DEFAULT_COMPOSITION)
    )

    def adjust_for_segregation(self, efficiency: float) -> 'WasteStream':
        """
        Adjusts the waste composition based on a segregation efficiency factor.

        This method assumes that improved segregation reduces certain hazardous fractions of the waste.
        For example, if needles/sharps plastic is segregated out more effectively, its fraction in the
        waste stream should be reduced proportionally to the efficiency value.

        Args:
            efficiency (float): A value between 0 and 1 representing the segregation efficiency.
                A value of 1 means no reduction (or 100% retention of the hazardous fraction),
                while values lower than 1 reduce the hazardous component.

        Returns:
            WasteStream: A new WasteStream instance with the adjusted composition.
        """
        # Create a deep copy of the current composition so as not to modify the original.
        new_comp = copy.deepcopy(self.composition)
        
        # Adjust the hazardous fractions based on the provided segregation efficiency.
        if "needles_sharps_plastic" in new_comp["organic_materials"]:
            new_comp["organic_materials"]["needles_sharps_plastic"] *= efficiency
        if "cytotoxic_organic" in new_comp["organic_materials"]:
            new_comp["organic_materials"]["cytotoxic_organic"] *= efficiency
        if "lab_reagents" in new_comp["chlorinated_materials"]:
            new_comp["chlorinated_materials"]["lab_reagents"] *= efficiency
        
        # Return a new WasteStream instance with the same mass but adjusted composition.
        return WasteStream(mass=self.mass, composition=new_comp)