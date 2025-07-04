import os
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from remote_docker_api import (
    trigger_docker_test,
    fetch_from_remote_container,
    upload_to_remote_container
)

router = APIRouter()

ALLOWED_EVM_EXTENSIONS = {".sol", ".txt"}
ALLOWED_NON_EVM_EXTENSIONS = {".wasm"}


def validate_extension(filename: str, allowed_extensions: set):
    ext = os.path.splitext(filename)[1].lower()
    if ext not in allowed_extensions:
        raise HTTPException(status_code=400, detail=f"File type {ext} not allowed.")


async def save_uploaded_file(file: UploadFile, subfolder: str) -> str:
    upload_dir = os.path.join("uploaded_contracts", subfolder)
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, file.filename)
    with open(file_path, "wb") as buffer:
        contents = await file.read()
        buffer.write(contents)
    return file_path


# Upload EVM
@router.post("/upload-evm")
async def upload_evm_contract(contract_file: UploadFile = File(...)):
    validate_extension(contract_file.filename, ALLOWED_EVM_EXTENSIONS)

    # Save locally
    saved_path = await save_uploaded_file(contract_file, "evm")

    # Upload to remote Docker container
    upload_to_remote_container(saved_path, "evm")

    # Run the contract test remotely
    logs = trigger_docker_test(contract_file.filename, "evm")

    # Fetch summary report
    summary_filename = f"test-summary-{contract_file.filename.replace('.sol', '')}.md"
    summary_content = fetch_from_remote_container(summary_filename, "evm")

    # Fetch aggregated report
    aggregated_content = fetch_from_remote_container("complete-contracts-report.md", "evm")

    # Optional: Read local contents
    with open(saved_path, "rb") as f:
        file_contents = f.read()

    result = process_evm_contract(file_contents, contract_file.filename)
    return JSONResponse(content={
        "message": "EVM contract processed",
        "filename": contract_file.filename,
        "docker_logs": logs,
        "test_summary": summary_content,
        "aggregated_report": aggregated_content,
        "details": result
    })


# Upload Non-EVM
@router.post("/upload-non-evm")
async def upload_non_evm_contract(contract_file: UploadFile = File(...)):
    validate_extension(contract_file.filename, ALLOWED_NON_EVM_EXTENSIONS)

    # Save locally
    saved_path = await save_uploaded_file(contract_file, "non-evm")

    # Upload to remote Docker container
    upload_to_remote_container(saved_path, "non-evm")

    # Run the contract test remotely
    logs = trigger_docker_test(contract_file.filename, "non-evm")

    # Fetch summary report
    summary_filename = f"test-summary-{contract_file.filename.replace('.wasm', '')}.md"
    summary_content = fetch_from_remote_container(summary_filename, "non-evm")

    # Fetch aggregated report
    aggregated_content = fetch_from_remote_container("complete-contracts-report.md", "non-evm")

    # Optional: Read local contents
    with open(saved_path, "rb") as f:
        file_contents = f.read()

    result = process_non_evm_contract(file_contents, contract_file.filename)
    return JSONResponse(content={
        "message": "Non-EVM contract processed",
        "filename": contract_file.filename,
        "docker_logs": logs,
        "test_summary": summary_content,
        "aggregated_report": aggregated_content,
        "details": result
    })


# Dummy processors (to be replaced with actual logic later)
def process_evm_contract(file_contents: bytes, filename: str) -> dict:
    return {"contract_type": "evm", "filename": filename, "status": "processed"}


def process_non_evm_contract(file_contents: bytes, filename: str) -> dict:
    return {"contract_type": "non-evm", "filename": filename, "status": "processed"}
