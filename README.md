# SmartTestHub – Backend API

A streamlined backend service that enables automated smart contract testing, security analysis, and reporting for both **EVM** and **non-EVM** platforms using a secure **remote Docker API**.

---

##  Architecture Overview

SmartTestHub now delegates all contract testing to a remote environment hosted at:
https://dockerapi.smarttesthub.live


This backend acts as a connector between:
- **Frontend** (e.g., [smart-test-hub.vercel.app](https://smart-test-hub.vercel.app))
- **Remote Docker API** that executes tests
- **User-uploaded contracts** and test reports

---

##  Backend Workflow

1. **File Upload**  
   Users upload `.sol` (EVM) or `.wasm` (non-EVM) files via `/upload-evm` or `/upload-non-evm`.

2. **Remote Storage**  
   Backend uploads the file to the remote Docker server using `upload_to_remote_container()`.

3. **Test Trigger**  
   It triggers contract analysis via `trigger_docker_test()` for the correct environment.

4. **Summary Retrieval**  
   The backend polls `fetch_from_remote_container()` until test summaries and reports are available.

5. **Frontend Integration**  
   JSON responses with logs and reports are returned to the frontend for display.

---

## API Endpoints

| Method | Endpoint              | Description                        |
|--------|-----------------------|------------------------------------|
| `GET`  | `/`                   | Health check                       |
| `POST` | `/upload-evm`         | Upload and test Solidity contract  |
| `POST` | `/upload-non-evm`     | Upload and test WASM contract      |

 

---

# Features

- Upload and process EVM (`.sol`) and Non-EVM (`.wasm`) smart contracts
- Uses a remote Docker service (`https://dockerapi.smarttesthub.live`) to test contracts
- Automatically retrieves contract-specific and aggregated reports
- Built with FastAPI and deployed on Render
- CORS-enabled for frontend access via Vercel

---

# Tech Stack

- Python 3.11
- FastAPI
- Uvicorn (ASGI server)
- Remote Docker API: `https://dockerapi.smarttesthub.live`
- Render (backend deployment)
- Vercel (frontend deployment)

---

📘 Swagger API docs:  


---

## Technologies Used

- **FastAPI** – High-performance Python web framework
- **Render** – Backend deployment
- **Vercel** – Frontend hosting
- **Remote Docker API** – Secure testing via `https://dockerapi.smarttesthub.live`

---

## Local Development CORS CONFIGURATION

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start the server locally
python main.py

Access your app at http://localhost:8000


## CORS CONFIGURATION

This backend allows access from:

allow_origins = [
  "http://localhost:8080",             # local dev
  "https://smart-test-hub.vercel.app" # deployed frontend
]


📁 Project Structure

SmartTestHub-Backend/
├── main.py
├── upload_routes.py
├── remote_docker_api.py
├── requirements.txt
├── render.yaml
├── .gitignore
├── uploaded_contracts/
├── test_summaries/


📬 Contact
Have questions or want to contribute?
📩 Email us: team@smarttesthub.live
