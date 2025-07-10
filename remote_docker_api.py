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
def fetch_from_remote_container(report_filename: str, contract_type: str, timeout: int = 60) -> str:
    """
    report_filename: e.g. 'Crowdfunding-report.md'
    contract_type: 'evm' or 'non-evm'
    """
    # pick the correct container
    container = "evm-container" if contract_type == "evm" else "non-evm-container"

    # now fetch the contract-specific report
    url = (
        f"https://dockerapi.smarttesthub.live"
        f"/containers/{container}/archive"
        f"?path=/app/logs/reports/{report_filename}"
    )
    print(f"🔍 Fetching TAR from: {url}")

    for second in range(timeout):
        resp = requests.get(url)
        if resp.status_code == 200:
            print(f"📦 TAR file received. Extracting '{report_filename}'…")
            try:
                tar_stream = io.BytesIO(resp.content)
                with tarfile.open(fileobj=tar_stream, mode="r:*") as tar:
                    member = next((m for m in tar.getmembers() if m.name.endswith(report_filename)), None)
                    if member:
                        content = tar.extractfile(member).read().decode()
                        return content
                    return f"❌ {report_filename} not found inside tar."
            except Exception as e:
                return f"❌ Error extracting TAR: {e}"
        elif resp.status_code == 404:
            print(f"⌛ Waiting for file ({second+1}/{timeout})…")
        else:
            return f"❌ Unexpected {resp.status_code}: {resp.text}"
        time.sleep(1)

    return f"❌ File '{report_filename}' not available after {timeout}s."