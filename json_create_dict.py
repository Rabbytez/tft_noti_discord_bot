import json

def organize_stage_data(data):
    """
    Organizes stage data from the input JSON by stages in a readable format.

    Parameters:
    - data: The JSON data containing "stage_data".

    Returns:
    - organized_data: A dictionary with stage identifiers as keys and stage data as values.
    """
    stage_data = data.get("stage_data", {})

    organized_data = {}

    if isinstance(stage_data, dict):
        # If stage_data is a dictionary, iterate over items
        for stage_key, stage_value in stage_data.items():
            # Safely access 'match_info'
            match_info = stage_value.get('match_info', {})
            # Safely access 'round_type'
            round_type = match_info.get('round_type', {})
            # Safely get 'stage'
            nested_stage = round_type.get('stage')

            if nested_stage is None:
                # Handle missing 'stage' key or 'round_type' key
                print(f"Warning: 'round_type' or 'stage' key is missing in 'match_info' for stage {stage_key}")
                continue  # Skip this stage since necessary data is missing

            # Now, you can add the stage data to organized_data
            organized_data[stage_key] = stage_value

    elif isinstance(stage_data, list):
        # If stage_data is a list, iterate over elements
        for stage_value in stage_data:
            # Safely access 'match_info'
            match_info = stage_value.get('match_info', {})
            # Safely access 'round_type'
            round_type = match_info.get('round_type', {})
            # Safely get 'stage'
            stage_key = round_type.get('stage')

            if stage_key is None:
                # Handle missing 'stage' key or 'round_type' key
                print("Warning: 'round_type' or 'stage' key is missing in 'match_info'")
                continue  # Skip this stage since necessary data is missing

            # Now, you can add the stage data to organized_data
            organized_data[stage_key] = stage_value

    else:
        # Handle cases where stage_data is neither a dict nor a list
        print("Warning: 'stage_data' is neither a dict nor a list.")
        # You may choose to handle this differently, such as raising an error

    return organized_data

if __name__ == "__main__":
    data = []
    # Organize the stage data
    organized_data = organize_stage_data(data)
