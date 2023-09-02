# GCB-August
Challenge files for the challenge featured during Gryphon's Cyber Blitz in August 2023


## Solution
Solution files can be found in the `./solution/` directory. 

A solve script has been provided at [solve.py](./solution/solve.py).
## Deployment

Ensure that you have a file named `.env` in the `./august/` directory with the following contents:

```
WEBHOOK_URL=YOUR-DISCORD-WEBHOOK-URL
FLAG=FLAG{FAKE_FLAG}
BOT_TOKEN=bot-token
ADMIN_TOKEN=admin-token
```

## Setup (Docker)

A `docker-compose.yml` has been provided to expadite the deployment process:
```bash
cd ./Gryphons-Cyber-Blitz/august/
sudo docker-compose up -d
```

The challenge web server will be listening on all interfaces at TCP/1337 (by default), you may change this at by editing `docker-compose.yml`.

## Setup (Manual)

Run the following commands to start the **webserver**:

[Python 3.9+](https://www.python.org/downloads/) or higher is required.

```bash
cd ./Gryphons-Cyber-Blitz/site/app/
python3 -m pip install -r requirements.txt
python3 app.py
```

This will start the challenge at http://localhost:1337/ by default.

Run the following commands to start the **xss admin bot**:

```bash
cd ./Gryphons-Cyber-Blitz/adminbot/
python3 -m pip install -r requirements.txt
playwright install --with-deps chromium
python bot.py 
```
