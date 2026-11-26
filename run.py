"""SAKHI local startup script.

Launches the integrated FastAPI server and serves the frontend application.
Can also be launched directly via:
    uvicorn src.api_link:app --host 127.0.0.1 --port 8000
"""

import uvicorn

if __name__ == "__main__":
    print("Starting SAKHI platform at http://127.0.0.1:8000 ...")
    uvicorn.run("src.api_link:app", host="127.0.0.1", port=8000, reload=True)
