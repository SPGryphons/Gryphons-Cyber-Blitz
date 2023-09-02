import logging

from dotenv import load_dotenv
from flask import Flask

load_dotenv()

from blueprints.routes import api, web
from database import restart_db_thread
from limiter import limiter
from webhook_logger import wh_logger

app = Flask(__name__)

# Register the blueprints
app.register_blueprint(web, url_prefix="/")
app.register_blueprint(api, url_prefix="/api")

@app.errorhandler(Exception)
def handle_exception(e):
    message = e.description if hasattr(e, "description") else [str(e) for a in e.args]
    response = {
        "error": {
            "type": e.__class__.__name__,
            "message": message
        }
    }

    logging.error(response)

    return response, e.code if hasattr(e, "code") else 500


if __name__ == "__main__":
    wh_logger.start()

    limiter.init_app(app)
    restart_db_thread.start()

    app.run(debug=False, host="0.0.0.0", port=1337)
    