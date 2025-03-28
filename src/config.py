# src/config.py
import copy
# ----------------------------------------------------------------------
# EMISSION FACTORS
# ----------------------------------------------------------------------
EMISSION_FACTORS = {
    "INCINERATION": {
        "carbon_content_fossil": 0.87,
        "carbon_content_biogenic": 0.47,
        "nitrogen_frac_organic": 0.025,
        "sulfur_frac_organic": 0.006,
        "so2_conversion": 0.85,
        "pm10_per_organic": 0.04,
        "pm25_per_organic": 0.03,
        "nox_per_waste": 0.08,
        "hg_volatilization": 0.90,
        "pb_volatilization": 0.35,
        "combustion_efficiency": 0.97,
        "excess_air_ratio": 1.4,
    },
    "LANDFILL": {
        "time_period": 100,
        "fast_decay_rate": 0.18,
        "slow_decay_rate": 0.02,
        "ch4_split": 0.50,
        "co2_split": 0.50,
        "nh3_split": 0.01,
        "nmvoc_split": 0.02,
        "hg_factor": 0.8,
        "pb_factor": 0.5,
    },
    "PYROLYSIS": {
        "co2_fossil_per_organic": 0.75,
        "ch4_fossil_per_organic": 0.06,
        "nmvoc_per_organic": 0.03,
        "pahs_per_organic": 0.001,
        "dioxin_per_chlorinated": 1e-14,
        "hg_per_mercury": 0.7,
        "pb_per_heavy_metal": 0.3,
    },
    # You can add additional process factors here (e.g., CHEM_DISINFECTION, AUTOCLAVE, MICROWAVE)
}

# ----------------------------------------------------------------------
# DEFAULT WASTE COMPOSITION
# ----------------------------------------------------------------------
DEFAULT_COMPOSITION = {
    "organic_materials": {
        "needles_sharps_plastic": 0.03,  # 0.30 * 0.1
        "body_fluids": 0.135,            # 0.15 * 0.9
        "lab_cultures": 0.095,           # 0.10 * 0.95
        "pharmaceuticals": 0.09,         # 0.10 * 0.9
        "cytotoxic_organic": 0.04,       # 0.05 * 0.8
    },
    "chlorinated_materials": {
        "lab_reagents": 0.075,           # 0.15 * 0.5
        "lab_cultures_disinfectants": 0.005,  # 0.10 * 0.05
        "pharmaceuticals_halogenated": 0.01,  # 0.10 * 0.1
        "cytotoxic_halogenated": 0.01,        # 0.05 * 0.2
    },
    "metallic_materials": {
        "needles_sharps_metal": 0.27,    # 0.30 * 0.9
        "body_fluids_metals": 0.015,     # 0.15 * 0.1
        "gas_cylinders": 0.0475,         # 0.05 * 0.95
        "mercury_waste": 0.025,          # 0.05 * 0.5
        "other_heavy_metals": 0.025,     # 0.05 * 0.5
    },
    "radioactive_materials": {
        "radioactive_metals": 0.045,     # 0.05 * 0.9
        "radioactive_organic": 0.005,    # 0.05 * 0.1
    },
}

# ----------------------------------------------------------------------
# HOSPITAL-SPECIFIC INDIRECT FACTORS
# ----------------------------------------------------------------------
HOSPITAL_INDIRECT_FACTORS = {
    "KBTH": {
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
    },
    "KATH": {
        "energy_inputs": {
            "energy_use_kWh_per_kg": 0.15,
            "co2_fossil_per_kWh": 0.50,
            "so2_per_kWh": 0.00020,
            "pm25_per_kWh": 0.00015,
        },
        "transportation": {
            "distance_km": 9,
            "truck_load_t": 10 * 0.310,
            "co2_fossil_per_tkm": 0.08,
            "nox_per_tkm": 0.0010,
        },
        "infrastructure": {
            "construction_co2_per_kg": 0.025,
            "land_use_factor": 0.0012,
        },
        "downstream": {
            "residue_ratio": 0.06 * 0.310,
            "residue_co2_per_kg": 0.22,
            "residue_so2_per_kg": 0.001,
        },
    },
    "CCTH": {
        "energy_inputs": {
            "energy_use_kWh_per_kg": 0.13,
            "co2_fossil_per_kWh": 0.48,
            "so2_per_kWh": 0.00018,
            "pm25_per_kWh": 0.00010,
        },
        "transportation": {
            "distance_km": 9.2,
            "truck_load_t": 10 * 0.122,
            "co2_fossil_per_tkm": 0.07,
            "nox_per_tkm": 0.0009,
        },
        "infrastructure": {
            "construction_co2_per_kg": 0.03,
            "land_use_factor": 0.0015,
        },
        "downstream": {
            "residue_ratio": 0.06 * 0.122,
            "residue_co2_per_kg": 0.18,
            "residue_so2_per_kg": 0.0011,
        },
    },
    "BRH": {
        "energy_inputs": {
            "energy_use_kWh_per_kg": 0.14,
            "co2_fossil_per_kWh": 0.52,
            "so2_per_kWh": 0.00020,
            "pm25_per_kWh": 0.00012,
        },
        "transportation": {
            "distance_km": 1.4,
            "truck_load_t": 10 * 0.100,
            "co2_fossil_per_tkm": 0.08,
            "nox_per_tkm": 0.0010,
        },
        "infrastructure": {
            "construction_co2_per_kg": 0.022,
            "land_use_factor": 0.0010,
        },
        "downstream": {
            "residue_ratio": 0.06 * 0.100,
            "residue_co2_per_kg": 0.21,
            "residue_so2_per_kg": 0.0010,
        },
    },
    "UCCH": {
        "energy_inputs": {
            "energy_use_kWh_per_kg": 0.13,
            "co2_fossil_per_kWh": 0.49,
            "so2_per_kWh": 0.00022,
            "pm25_per_kWh": 0.00011,
        },
        "transportation": {
            "distance_km": 4.7,
            "truck_load_t": 10 * 0.023,
            "co2_fossil_per_tkm": 0.08,
            "nox_per_tkm": 0.0012,
        },
        "infrastructure": {
            "construction_co2_per_kg": 0.018,
            "land_use_factor": 0.0009,
        },
        "downstream": {
            "residue_ratio": 0.06 * 0.023,
            "residue_co2_per_kg": 0.21,
            "residue_so2_per_kg": 0.00095,
        },
    },
}

# ----------------------------------------------------------------------
# IMPACT CATEGORIES & NORMALIZATION FACTORS (for LCIA)
# ----------------------------------------------------------------------
IMPACT_CATEGORIES = {
    "Human Toxicity (HT)": (
        'CML v4.8 2016', 'human toxicity', 'human toxicity (HTP inf)'
    ),
    "Climate Change (CC)": (
        'CML v4.8 2016', 'climate change', 'global warming potential (GWP100)'
    ),
    "Eutrophication (EP)": (
        'CML v4.8 2016', 'eutrophication', 'eutrophication (fate not incl.)'
    ),
    "Acidification (AP)": (
        'CML v4.8 2016', 'acidification', 'acidification (incl. fate, average Europe total, A&B)'
    ),
    "Marine Aquatic Eco-Toxicity (MAE)": (
        'CML v4.8 2016', 'ecotoxicity: marine', 'marine aquatic ecotoxicity (MAETP inf)'
    ),
    "Terrestrial Eco-Toxicity (TE)": (
        'CML v4.8 2016', 'ecotoxicity: terrestrial', 'terrestrial ecotoxicity (TETP inf)'
    ),
    "Freshwater Eco-Toxicity (FAE)": (
        'CML v4.8 2016', 'ecotoxicity: freshwater', 'freshwater aquatic ecotoxicity (FAETP inf)'
    ),
    "Photochemical Oxidation (PO)": (
        'CML v4.8 2016', 'photochemical oxidant formation', 'photochemical oxidation (high NOx)'
    ),
}

NORMALIZATION_FACTORS = {
    "Human Toxicity (HT)": 8.86e12,
    "Climate Change (CC)": 4.18e12,
    "Eutrophication (EP)": 3.77e9,
    "Acidification (AP)": 3.36e11,
    "Marine Aquatic Eco-Toxicity (MAE)": 6.24e12,
    "Terrestrial Eco-Toxicity (TE)": 5.09e10,
    "Freshwater Eco-Toxicity (FAE)": 3.07e10,
    "Photochemical Oxidation (PO)": 3.51e11,
}