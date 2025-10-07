# Logitech Z407 Remote Controller

This is an small web application for controlling the Logitech Z407 speakers based off the work from [freundTech's reverse engineering work](https://github.com/freundTech/logi-z407-reverse-engineering). To run this application, this program requires you to have bluetooth on the device you plan to run this on.

I was able to successfully run this on my Raspberry Pi 5 using the [docker-compose.yml](https://github.com/angelolz/z407-controller/blob/main/docker-compose.yml) file.

# Setup

## Docker (recommended)

1. Save the [docker-compose.yml](https://raw.githubusercontent.com/angelolz/z407-controller/refs/heads/main/docker-compose.yml) to a file.
2. Open up a terminal and navigate to where you've saved the file and run `docker compose up`.

## Outside of docker or for local development

1. Clone this repo. Navigate to the folder created for the repo.
2. Set up a virtual environment.
    ```
    python3 -m venv venv
    source venv/bin/activate
    ```
3. Install dependencies with `pip install -r requirements.txt`
4. Run the server with `uvicorn main:app --host 0.0.0.0 --port 8000`

You can access the front end controller with `http://<your_local_ip_address>:8000`. If you'd like to integrate this into another application, the API is also accessible to you, the documentation is in: `http://<your_local_ip_address>:8000/docs`.
