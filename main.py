from flask import Flask, request
import os
from dotenv import load_dotenv
from db import setup_db
from controller import process_webhook_update 

load_dotenv()
app = Flask(__name__)
setup_db()

# @app.route('/', methods=['POST'])
# def webhook():
#     update = telegram.Update.de_json(request.get_json(force=True), bot)
#     return 'OK'

@app.route('/', methods=['POST'])
async def webhook():
    await process_webhook_update(request)
    return "OK"


# Path to check if server is up
@app.route('/health', methods=['GET'])
def health_check():
    return 'OK'

# @app.route('/set_webhook', methods=['GET', 'POST'])
# def set_webhook():
#     success = application.bot.set_webhook(os.getenv('WEBHOOK_URL'))
#     if success:
#         return "Webhook set successfully"
#     else:
#         return "Webhook setup failed"

# Run the app
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))