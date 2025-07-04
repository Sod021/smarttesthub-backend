import time
import requests
import os

# Remote Docker API server
REMOTE_API_BASE_URL = "https://dockerapi.smarttesthub.live"

# Upload file to the remote Docker container
def upload_to_remote_container(local_path: str, contract_type: str):
    url = f"{REMOTE_API_BASE_URL}/upload/{contract_type}"
    with open(local_path, "rb") as file:
        files = {"file": (os.path.basename(local_path), file)}
        response = requests.post(url, files=files)

    if response.status_code != 200:
        raise Exception(f"Upload failed: {response.status_code} - {response.text}")
    return response.json()


# Trigger a remote test execution
def trigger_docker_test(filename: str, contract_type: str) -> str:
    url = f"{REMOTE_API_BASE_URL}/trigger-test"
    data = {
        "filename": filename,
        "contract_type": contract_type
    }
    response = requests.post(url, json=data)
    if response.status_code != 200:
        return f"❌ Remote execution failed: {response.status_code} - {response.text}"
    return f"✅ Test triggered:\n{response.text}"


# Fetch result file from remote container (with polling)
def fetch_from_remote_container(filename: str, contract_type: str, timeout: int = 60) -> str:
    url = f"{REMOTE_API_BASE_URL}/download/{contract_type}/{filename}"

    for second in range(timeout):
        response = requests.get(url)

        if response.status_code == 200:
            return response.text

        time.sleep(1)

    return f"❌ File '{filename}' not available after waiting {timeout} seconds."
