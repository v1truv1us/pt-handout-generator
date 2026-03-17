import json
import os
from config import CANDIDATES_FILE, SELECTED_FILE


def select_images():
    if not os.path.exists(CANDIDATES_FILE):
        print(f"Error: {CANDIDATES_FILE} not found. Run 'discover' first.")
        return None

    with open(CANDIDATES_FILE, "r") as f:
        candidates_data = json.load(f)

    selected = {}

    for exercise in candidates_data:
        exercise_id = exercise["id"]
        top_candidate = None

        if exercise.get("candidates"):
            top_candidate = exercise["candidates"][0]

        selected[exercise_id] = {
            "name": exercise["name"],
            "source_page": exercise["source_page"],
            "reps": exercise["reps"],
            "selected_url": top_candidate["url"] if top_candidate else None,
            "alt_text": top_candidate["alt"] if top_candidate else None,
            "local_path": None,
        }

        if top_candidate:
            print(f"Selected for {exercise['name']}: {top_candidate['url'][:60]}...")
        else:
            print(f"Warning: No candidates for {exercise['name']}")

    with open(SELECTED_FILE, "w") as f:
        json.dump(selected, f, indent=2)

    print(f"\nSelections saved to {SELECTED_FILE}")
    print("You can edit this file to change URLs or add local paths.")
    return selected
