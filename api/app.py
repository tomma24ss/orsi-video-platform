from flask import Flask, jsonify
from flask_cors import CORS
from controllers.video_controller import video_blueprint
from utils.logger import logger
from exceptions.api_exceptions import APIException
from config import DevelopmentConfig
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

# Load configuration
app.config.from_object(DevelopmentConfig)

# Setup CORS with config values
CORS(app, resources={r"/videos/*": {"origins": app.config['CORS_ORIGINS']}}, supports_credentials=True)

# Register Blueprints
app.register_blueprint(video_blueprint)

# Global Error Handler
@app.errorhandler(APIException)
def handle_api_exception(error):
    logger.error(f"API Error: {error}")
    return jsonify({"error": str(error)}), error.status_code

@app.errorhandler(Exception)
def handle_general_exception(error):
    logger.error(f"Unhandled Exception: {error}")
    return jsonify({"error": "An unexpected error occurred."}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=app.config['DEBUG'])
