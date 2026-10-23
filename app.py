import os
import threading

from flask import Flask

from Jannat_Makon_Bot.bot import main as start_bot

app = Flask(__name__)


@app.get("/")
def home():
    return {"status": "ok", "service": "telegram-bot"}


@app.get("/health")
def health():
    return {"status": "ok"}


def run_bot_in_background():
    start_bot()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "10000"))
    threading.Thread(target=run_bot_in_background, daemon=True).start()
    app.run(host="0.0.0.0", port=port)
