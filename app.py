import os
from threading import Thread

from flask import Flask

from Jannat_Makon_Bot.bot import main as start_bot

app = Flask(__name__)


@app.get("/")
def home():
    return {"status": "ok", "service": "telegram-bot"}


@app.get("/health")
def health():
    return {"status": "ok"}


def run_web_server():
    port = int(os.environ.get("PORT", "10000"))
    app.run(host="0.0.0.0", port=port, use_reloader=False)


if __name__ == "__main__":
    web_thread = Thread(target=run_web_server, daemon=True)
    web_thread.start()
    start_bot()
