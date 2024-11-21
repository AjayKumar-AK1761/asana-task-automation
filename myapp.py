# main.py
import requests
from flask import Flask, request, jsonify
from required_ids import ASANA_API_TOKEN, SECTION_IDS

app = Flask(__name__)

def update_task_name(task_id, new_name):
    """
    Updates the name of a specific task in Asana.
    """
    url = f"https://app.asana.com/api/1.0/tasks/{task_id}"
    headers = {
        "Authorization": f"Bearer {ASANA_API_TOKEN}"
    }
    data = {
        "name": new_name
    }
    response = requests.put(url, headers=headers, json=data)
    if response.status_code == 200:
        print(f"Task {task_id} renamed to '{new_name}'")
    else:
        print(f"Failed to rename task {task_id}: {response.status_code}, {response.text}")

@app.route("/webhook", methods=["POST"])
def webhook_handler():
    """
    Handles incoming webhook events from Asana.
    """
    payload = request.json

    # Extract task and section data
    events = payload.get("events", [])
    for event in events:
        if event["type"] == "task" and event["action"] == "changed":
            # Fetch task details
            task_id = event["resource"]
            task_data = get_task_details(task_id)

            # Check if the task has moved to the "In Progress" section
            if task_data["memberships"][0]["section"]["gid"] == SECTION_IDS["In Progress"]:
                # Add " -_-" to the task name
                current_name = task_data["name"]
                if " -_-" not in current_name:
                    new_name = f"{current_name} -_-"
                    update_task_name(task_id, new_name)

    return jsonify({"status": "success"})

def get_task_details(task_id):
    """
    Fetch details of a specific task from Asana.
    """
    url = f"https://app.asana.com/api/1.0/tasks/{task_id}"
    headers = {
        "Authorization": f"Bearer {ASANA_API_TOKEN}"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()["data"]
    else:
        print(f"Failed to fetch task details: {response.status_code}, {response.text}")
        return {}

if __name__ == "__main__":
    app.run(port=5000)
