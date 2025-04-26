# Logitech Z407 Remote Controller API
This is an API server based off the work from [freundTech's reverse engineering work](https://github.com/freundTech/logi-z407-reverse-engineering). Huge props to them for the amazing work there.

# Setup
1. Clone this repo. Navigate to the folder created for the repo.
2. Set up a virtual environment.
    ```
    python3 -m venv venv
    source venv/bin/activate
    ```
3. Install dependencies with `pip install -r requirements.txt`
4. Run the server with `uvicorn main:app --host 0.0.0.0 --port 8000`

You can see the api endpoints with `http://<your_local_ip_address>:8000/docs`.
