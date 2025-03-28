# HospitalWasteManagement/src/main.py

import logging
from pathlib import Path
import csv
import brightway2 as bw
import pint

from src import config
from src.waste_stream import WasteStream
from src.processes.incineration import IncinerationProcess
from src.processes.landfill import LandfillProcess
from src.processes.pyrolysis import PyrolysisProcess
from src.processes.chem_disinfection import ChemDisinfectionProcess
from src.processes.autoclave import AutoclaveProcess
from src.processes.microwave import MicrowaveProcess
from src.indirect import IndirectEmissionsCalculator
from src.database import (
    setup_project,
    build_flow_index,
    retrieve_flows,
    create_or_reset_db,
    create_activity,
    add_production_exchange,
    add_biosphere_exchanges
)
from src.lcia import compute_lcia

# Initialize a Pint unit registry.
ureg = pint.UnitRegistry()

def main():
    # Configure logging.
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    
    # Set up the Brightway2 project and ensure the biosphere database is loaded.
    project_name = "HospitalWasteManagement"
    bio_db = setup_project(project_name)
    flow_index = build_flow_index(bio_db)
    flows = retrieve_flows(flow_index)
    
    # Create or reset the Hospital Processes database.
    process_db_name = "HospitalProcesses"
    process_db = create_or_reset_db(process_db_name)
    
    # Define hospitals (each with a name and waste mass in kg).
    hospitals = [
        {"name": "KBTH", "waste": 2174},
        {"name": "KATH", "waste": 1535},
        {"name": "CCTH", "waste": 600},
        {"name": "BRH", "waste": 495},
        {"name": "UCCH", "waste": 113},
    ]
    
    # Define a full set of scenarios.
    scenarios = {
        "BASELINE": {
            "description": "Reflects current real-world practice, moderate segregation (~50%), older incineration, minimal enforcement.",
            "segregation_efficiency": 0.5,
            "incineration_flue_gas_efficiency": 0.0,
            "energy_policy_factor": 0.0,
            "landfill_best_practices": False,
            "biomedical_risk_factor": 0.8,
            "chemical_disinfection_fraction": 0.5
        },
        "ENHANCED_INCINERATION": {
            "description": "Better segregation (~80%), partial flue-gas cleaning, moderate compliance.",
            "segregation_efficiency": 0.8,
            "incineration_flue_gas_efficiency": 0.5,
            "energy_policy_factor": 0.2,
            "landfill_best_practices": False,
            "biomedical_risk_factor": 0.4,
            "chemical_disinfection_fraction": 0.2
        },
        "COMPREHENSIVE_ALTS": {
            "description": "High segregation (~90%), mix of autoclave/chem disinfection, incineration only for certain streams, improved compliance.",
            "segregation_efficiency": 0.9,
            "incineration_flue_gas_efficiency": 0.7,
            "energy_policy_factor": 0.3,
            "landfill_best_practices": True,
            "biomedical_risk_factor": 0.2,
            "chemical_disinfection_fraction": 0.1
        },
        "HIGH_TECH": {
            "description": "State-of-the-art incinerators with advanced controls, near-optimal segregation (≥95%), very strict enforcement.",
            "segregation_efficiency": 0.95,
            "incineration_flue_gas_efficiency": 0.9,
            "energy_policy_factor": 0.4,
            "landfill_best_practices": True,
            "biomedical_risk_factor": 0.1,
            "chemical_disinfection_fraction": 0.05
        },
        "POLICY_NETZERO": {
            "description": "Circular economy principles, material/energy recovery, carbon offsets, near-optimal segregation.",
            "segregation_efficiency": 0.95,
            "incineration_flue_gas_efficiency": 0.95,
            "energy_policy_factor": 0.5,
            "landfill_best_practices": True,
            "biomedical_risk_factor": 0.05,
            "chemical_disinfection_fraction": 0.05
        },
        "CATASTROPHIC": {
            "description": "Worst-case: Very poor segregation, uncontrolled incineration or open burning, minimal regulation.",
            "segregation_efficiency": 0.2,
            "incineration_flue_gas_efficiency": 0.0,
            "energy_policy_factor": 0.0,
            "landfill_best_practices": False,
            "biomedical_risk_factor": 0.9,
            "chemical_disinfection_fraction": 0.8
        }
    }
    
    # Initialize treatment process classes using the corresponding emission factors.
    processes = {
        "INCINERATION": IncinerationProcess("Incineration", config.EMISSION_FACTORS["INCINERATION"]),
        "LANDFILL": LandfillProcess("Landfill", config.EMISSION_FACTORS["LANDFILL"]),
        "PYROLYSIS": PyrolysisProcess("Pyrolysis", config.EMISSION_FACTORS["PYROLYSIS"]),
        "CHEM_DISINFECTION": ChemDisinfectionProcess("Chemical Disinfection", config.EMISSION_FACTORS.get("CHEM_DISINFECTION", {})),
        "AUTOCLAVE": AutoclaveProcess("Autoclave", config.EMISSION_FACTORS.get("AUTOCLAVE", {})),
        "MICROWAVE": MicrowaveProcess("Microwave", config.EMISSION_FACTORS.get("MICROWAVE", {}))
    }
    
    # Dictionary to store results.
    results = {}
    
    # Loop over scenarios, hospitals, and processes.
    for scenario_name, scen in scenarios.items():
        logging.info(f"Running scenario: {scenario_name} - {scen['description']}")
        results[scenario_name] = {}
        for hospital in hospitals:
            hosp_name = hospital["name"]
            results[scenario_name][hosp_name] = {}
            
            # Create a waste stream object for the hospital.
            waste_mass = hospital["waste"] * ureg("kg")
            waste_stream = WasteStream(mass=waste_mass)
            adjusted_waste = waste_stream.adjust_for_segregation(scen["segregation_efficiency"])
            
            # Set up the indirect emissions calculator if hospital-specific factors exist.
            indirect_factors = config.HOSPITAL_INDIRECT_FACTORS.get(hosp_name, {})
            indirect_calc = IndirectEmissionsCalculator(indirect_factors) if indirect_factors else None
            
            for process_key, process_obj in processes.items():
                # Create a unique activity for each hospital-process-scenario combination.
                activity_code = f"{hosp_name}_{process_key}_{scenario_name}"
                activity_name = f"{hosp_name} {process_key} {scenario_name}"
                activity = create_activity(process_db, activity_code, activity_name)
                add_production_exchange(activity)
                
                # Calculate direct emissions using the process model.
                direct_emissions = process_obj.calculate_direct_emissions(adjusted_waste, scenario=scen)
                
                # Add indirect emissions if applicable.
                if indirect_calc:
                    indirect_emissions = indirect_calc.calculate(adjusted_waste)
                    # Combine direct and indirect emissions.
                    for key, val in indirect_emissions.items():
                        if key in direct_emissions:
                            direct_emissions[key] += val
                        else:
                            direct_emissions[key] = val
                
                # Create biosphere exchanges based on the combined emissions.
                add_biosphere_exchanges(activity, direct_emissions, flows)
                
                # Compute LCIA scores for the activity for each impact category.
                results[scenario_name][hosp_name][process_key] = {}
                for category, method in config.IMPACT_CATEGORIES.items():
                    if method not in bw.methods:
                        logging.warning(f"LCIA method {method} not found for impact category {category}.")
                        results[scenario_name][hosp_name][process_key][category] = None
                    else:
                        score = compute_lcia(activity, method)
                        norm_factor = config.NORMALIZATION_FACTORS.get(category, 1)
                        normalized = score / norm_factor if norm_factor != 0 else None
                        results[scenario_name][hosp_name][process_key][category] = (score, normalized)
    
    # Export the results to a CSV file.
    output_file = Path("scenario_results.csv")
    with output_file.open("w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Scenario", "Hospital", "Process", "Impact Category", "Raw Score", "Normalized Score"])
        for scenario_name, hosp_data in results.items():
            for hosp_name, proc_data in hosp_data.items():
                for process_key, impact_data in proc_data.items():
                    for category, scores in impact_data.items():
                        if scores is None:
                            writer.writerow([scenario_name, hosp_name, process_key, category, None, None])
                        else:
                            raw, norm = scores
                            writer.writerow([scenario_name, hosp_name, process_key, category, raw, norm])
    
    logging.info(f"Scenario results exported to {output_file}")

if __name__ == "__main__":
    main()