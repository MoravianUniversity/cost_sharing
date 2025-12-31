import os
import sys
from flask import Flask
from dotenv import load_dotenv
from cost_sharing.oauth_handler import OAuthHandler
from cost_sharing.storage import InMemoryCostStorage
from cost_sharing.cost_sharing import CostSharing


def create_app(oauth_handler, application):
    """
    Create and configure Flask application.

    Args:
        oauth_handler: OAuthHandler instance for OAuth operations
        application: CostSharing application layer instance

    Returns:
        Configured Flask application
    """
    app = Flask(__name__)

    @app.route('/')
    def index():
        return "Hello, World!"

    return app


# This is "main" for the gunicorn launch and cannot be tested directly
def launch():  # pragma: no cover
    """Launch the Flask application with environment configuration."""
    # Load environment variables from .env file
    load_dotenv()

    # Validate required environment variables
    for var in ['BASE_URL', 'GOOGLE_CLIENT_ID', 'GOOGLE_CLIENT_SECRET', 'JWT_SECRET']:
        if not os.getenv(var):
            print(f"Error: Missing required environment variable: {var}", file=sys.stderr)
            sys.exit(1)

    oauth_handler = OAuthHandler(
        base_url=os.getenv('BASE_URL'),
        google_client_id=os.getenv('GOOGLE_CLIENT_ID'),
        google_client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
        jwt_secret=os.getenv('JWT_SECRET')
    )

    return create_app(oauth_handler, CostSharing(InMemoryCostStorage()))


# This is "main" for the local launch and can be tested directly
if __name__ == '__main__':  # pragma: no cover
    launch().run(debug=True, port=8000)
