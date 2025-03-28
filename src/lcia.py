# HospitalWasteManagement/src/lcia.py

import logging
import brightway2 as bw

def compute_lcia(activity: bw.Activity, method: tuple) -> float:
    """
    Computes the Life Cycle Impact Assessment (LCIA) score for a given activity using a specified LCIA method.

    Args:
        activity (bw.Activity): The Brightway2 activity for which the LCIA is calculated.
        method (tuple): The LCIA method tuple (e.g., ('CML v4.8 2016', 'climate change', 'global warming potential (GWP100)')).

    Returns:
        float: The computed LCIA score for one unit of the activity.
        
    In case of any errors during the calculation, the function logs the error and returns 0.0.
    """
    try:
        # Create an LCA object with the activity as the functional unit.
        lca = bw.LCA({activity: 1}, method)
        lca.lci()    # Calculate the life cycle inventory.
        lca.lcia()   # Calculate the life cycle impact assessment.
        return lca.score
    except Exception as e:
        logging.error(f"Error computing LCIA for activity '{activity['name']}': {e}")
        return 0.0
