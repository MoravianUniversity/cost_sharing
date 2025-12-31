import os
import sys
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from cost_sharing.oauth_handler import (
    OAuthHandler, OAuthCodeError, OAuthVerificationError
)
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

    @app.route('/auth/callback', methods=['GET'])
    def auth_callback():
        """
        Handle OAuth callback from Google.

        Extracts the authorization code, exchanges it for user info, creates/gets user,
        and returns a JWT token along with user information.
        """
        # Extract code from query parameters
        code = request.args.get('code')
        if not code:
            return jsonify({
                "error": "Validation failed",
                "message": "code parameter is required"
            }), 400

        try:
            # Exchange OAuth code for user information
            user_info = oauth_handler.exchange_code_for_user_info(code)
            email = user_info['email']
            name = user_info['name']

            # Get or create user in the application
            user = application.get_or_create_user(email, name)

            # Create JWT token for the user
            token = oauth_handler.create_jwt_token(user.id)

            # Return token and user information
            return jsonify({
                "token": token,
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "name": user.name
                }
            }), 200

        except OAuthCodeError:
            return jsonify({
                "error": "Validation failed",
                "message": "Invalid or expired authorization code"
            }), 400

        except OAuthVerificationError:
            return jsonify({
                "error": "Unauthorized",
                "message": "OAuth verification failed"
            }), 401

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
