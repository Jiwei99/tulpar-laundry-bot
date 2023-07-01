from telegram import Update
from flask import Flask, request
import os
from dotenv import load_dotenv
from db import setup_db
from controller import create_bot 

load_dotenv()
app = Flask(__name__)
setup_db()
application = create_bot()

# @app.route('/', methods=['POST'])
# def webhook():
#     update = telegram.Update.de_json(request.get_json(force=True), bot)
#     return 'OK'

@app.route('/', methods=['POST'])
def webhook():
    application.process_update(
        Update.de_json(data=request.json(), bot=application.bot)
    )
    return "OK"


# Path to check if server is up
@app.route('/health', methods=['GET'])
def health_check():
    return 'OK'

@app.route('/set_webhook', methods=['GET', 'POST'])
def set_webhook():
    success = application.bot.set_webhook(os.getenv('WEBHOOK_URL'))
    if success:
        return "Webhook set successfully"
    else:
        return "Webhook setup failed"

# Run the app
if __name__ == '__main__':
    app.run()