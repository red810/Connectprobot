# server.py
import threading
import os
from flask import Flask, jsonify
from main import build_app
import db
import asyncio
import logging

logging.basicConfig(level=logging.INFO)

app = Flask("ConnectProBot")

@app.route("/")
def home():
    return """
    <html>
      <head><title>ConnectProBot</title></head>
      <body style="font-family: Arial; text-align:center; padding:40px;">
        <h1>✅ ConnectProBot is Running!</h1>
        <p>Bot runs via polling. Use /start to interact.</p>
      </body>
    </html>
    """, 200

@app.route("/status")
def status():
    return jsonify({"status": "running", "bot": os.getenv("BOT_USERNAME", "unknown")}), 200

def run_flask():
    port = int(os.getenv("PORT", "5000"))
    # Use 0.0.0.0 for container environments
    app.run(host="0.0.0.0", port=port)

def run_bot_loop():
    """Start the telegram bot in the same process using asyncio."""
    db.init_db()
    async def _run():
        application = build_app()
        await application.run_polling()
    asyncio.run(_run())

if __name__ == "__main__":
    # start flask in separate thread
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    # run bot (blocking)
    run_bot_loop()
