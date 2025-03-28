# HospitalWasteManagement/src/processes/base.py
from abc import ABC, abstractmethod
from typing import Dict, Any
import pint

# Initialize the Pint unit registry.
ureg = pint.UnitRegistry()

class TreatmentProcess(ABC):
    """
    Base class for treatment processes in the Hospital Waste Management LCA framework.
    
    Each treatment process should inherit from this class and implement the
    calculate_direct_emissions method, which computes the process-specific direct emissions
    for a given waste stream and scenario.
    
    Attributes:
        name (str): The name of the treatment process.
        factors (Dict[str, Any]): A dictionary containing process-specific factors (e.g., emission factors).
    """
    def __init__(self, name: str, factors: Dict[str, Any]):
        self.name = name
        self.factors = factors

    @abstractmethod
    def calculate_direct_emissions(self, waste, scenario: Dict[str, Any] = None) -> Dict[str, pint.Quantity]:
        """
        Calculate the direct emissions for this treatment process given a waste stream and an optional scenario.
        
        Args:
            waste: An object representing the waste stream. Typically, this object will have attributes such as mass
                   and composition (e.g., an instance of the WasteStream class).
            scenario (Dict[str, Any], optional): A dictionary of scenario parameters that may modify emission factors.
        
        Returns:
            Dict[str, pint.Quantity]: A dictionary mapping emission keys (e.g., 'co2_fossil', 'so2') to their calculated amounts
                                      as Pint quantities.
        """
        pass
