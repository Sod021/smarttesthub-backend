import io
import tarfile
import requests
import os
import time

# Docker API expects archive at this endpoint
DOCKER_API_URL = "https://dockerapi.smarttesthub.live/containers/evm-container/archive?path=/app/input"
HEADERS = {"Content-Type": "application/x-tar"}

# ✅ Create .tar from in-memory file and PUT to Docker API
def upload_to_remote_container_memory(file_bytes: bytes, filename: str, contract_type: str):
    tar_stream = io.BytesIO()

    # Create in-memory .tar
    with tarfile.open(fileobj=tar_stream, mode="w") as tar:
        tarinfo = tarfile.TarInfo(name=filename)
        tarinfo.size = len(file_bytes)
        tar.addfile(tarinfo, io.BytesIO(file_bytes))
    
    tar_stream.seek(0)

    # PUT to Docker API directly
    response = requests.put(DOCKER_API_URL, headers=HEADERS, data=tar_stream)

    if response.status_code != 200:
        raise Exception(f"Upload to Docker failed: {response.status_code} - {response.text}")
    
    return {"status": "success", "message": "File uploaded and extracted to container"}


# Trigger a remote test execution
def trigger_docker_test(filename: str, contract_type: str) -> str:
    url = f"{DOCKER_API_URL}/trigger-test"
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
    container_name = "evm-container"  # Both evm and non-evm go to same container now
    if contract_type == "non-evm":
        container_name = "non-evm-container"  # only if they are split

    #path = f"/app/logs/reports/{filename}"
    #url = f"{DOCKER_API_URL}/containers/{container_name}/archive?path={path}"
    url = "https://dockerapi.smarttesthub.live/containers/evm-container/archive?path=/app/logs/reports/complete-contracts-report.md"
    url = "https://dockerapi.smarttesthub.live/containers/non-evm-container/archive?path=/app/logs/reports/complete-contracts-report.md"

    print(f"🔍 Fetching TAR from: {url}")

    for second in range(timeout):
        response = requests.get(url)
        
        if response.status_code == 200:
            print(f"📦 TAR file received. Extracting '{filename}'...")
            try:
                tar_data = io.BytesIO(response.content)
                with tarfile.open(fileobj=tar_data) as tar:
                    for member in tar.getmembers():
                        if member.name.endswith(filename):
                            extracted = tar.extractfile(member)
                            if extracted:
                                content = extracted.read().decode("utf-8")
                                return content
            except Exception as e:
                return f"❌ Error extracting TAR: {str(e)}"

        elif response.status_code == 404:
            print(f"⌛ Waiting for file ({second + 1}/{timeout})...")
        else:
            return f"❌ Unexpected response: {response.status_code} - {response.text}"

        time.sleep(1)

    return f"❌ File '{filename}' not available after waiting {timeout} seconds."