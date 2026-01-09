import os
import sys
import functools
import sqlite3
from flask import Flask, request, jsonify, g, render_template
from dotenv import load_dotenv
from cost_sharing.oauth_handler import (
    OAuthHandler, OAuthCodeError, OAuthVerificationError,
    TokenExpiredError, TokenInvalidError
)
from cost_sharing.db_storage import DatabaseCostStorage
from cost_sharing.cost_sharing import CostSharing
from cost_sharing.validation import (
    validate_json_body,
    validate_required_string,
    validate_optional_string,
    validate_required_query_param
)


# Ignore "too-many-statements" and "Too many local variables"
# because this function is going to be long!
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

    def require_auth(f):
        """
        Decorator to require JWT authentication for a route.

        Extracts and validates JWT token from Authorization header.
        Stores user_id in Flask's g object for use in the route handler.
        Returns 401 Unauthorized if authentication fails.
        """
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            # Extract Authorization header
            auth_header = request.headers.get('Authorization')
            if not auth_header:
                return jsonify({
                    "error": "Unauthorized",
                    "message": "Authentication required"
                }), 401

            # Check if header starts with "Bearer "
            if not auth_header.startswith('Bearer '):
                return jsonify({
                    "error": "Unauthorized",
                    "message": "Authentication required"
                }), 401

            # Extract token
            token = auth_header[7:]  # Remove "Bearer " prefix

            try:
                # Validate token and get user_id
                user_id = oauth_handler.validate_jwt_token(token)
                # Store user_id in g for use in route handler
                g.user_id = user_id
            except (TokenExpiredError, TokenInvalidError):
                return jsonify({
                    "error": "Unauthorized",
                    "message": "Authentication required"
                }), 401

            # Call the original route function
            return f(*args, **kwargs)

        return decorated_function

    @app.route('/')
    def index():
        """Serve the demo page."""
        return render_template('index.html')

    @app.route('/auth/login', methods=['GET'])
    def auth_login():
        """
        Get Google OAuth authorization URL.

        Returns the URL that the frontend should redirect to for Google OAuth login.
        """
        authorization_url, state = oauth_handler.get_authorization_url()
        return jsonify({
            "url": authorization_url,
            "state": state
        }), 200

    @app.route('/auth/callback', methods=['GET'])
    def auth_callback():
        """
        Handle OAuth callback from Google.

        Exchanges authorization code for user info, creates/gets user, and returns JWT token.
        Called by JavaScript fetch after Google redirects to main page with code.
        """
        # Validate code query parameter
        code, error = validate_required_query_param(request, 'code')
        if error is not None:
            return error

        try:
            # Exchange OAuth code for user information
            user_info = oauth_handler.exchange_code_for_user_info(code)
            email = user_info['email']
            name = user_info['name']

            # Get or create user in the application
            user = application.get_or_create_user(email, name)

            # Create JWT token for the user
            token = oauth_handler.create_jwt_token(user.id)

            # Return token and user information as JSON
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

    @app.route('/auth/me', methods=['GET'])
    @require_auth
    def auth_me():
        """
        Get current authenticated user information.

        Requires valid JWT token in Authorization header.
        Returns user information (id, email, name).
        """
        # Get user_id from g (set by require_auth decorator)
        user_id = g.user_id

        # Get user from application layer
        user = application.get_user_by_id(user_id)

        # Return user information
        return jsonify({
            "id": user.id,
            "email": user.email,
            "name": user.name
        }), 200

    @app.route('/groups', methods=['GET'])
    @require_auth
    def get_groups():
        """
        Get all groups that the authenticated user belongs to.

        Requires valid JWT token in Authorization header.
        Returns list of group summaries (id, name, description, memberCount).
        """
        # Get user_id from g (set by require_auth decorator)
        user_id = g.user_id

        # Get user's groups from application layer
        groups = application.get_user_groups(user_id)

        # Convert GroupInfo objects to JSON format
        groups_json = [
            {
                "id": group.id,
                "name": group.name,
                "description": group.description,
                "memberCount": group.member_count
            }
            for group in groups
        ]

        # Return groups in the format specified by API spec
        return jsonify({
            "groups": groups_json
        }), 200

    @app.route('/groups', methods=['POST'])
    @require_auth
    def create_group():
        """
        Create a new group with the authenticated user as creator and member.

        Requires valid JWT token in Authorization header.
        Request body must contain 'name' (required, 1-100 chars) and
        optionally 'description' (max 500 chars).
        Returns 201 with group information including creator and member count.
        """
        # Get user_id from g (set by require_auth decorator)
        user_id = g.user_id

        # Validate JSON body
        data, error = validate_json_body(request)
        if error is not None:
            return error

        # Validate name
        name, error = validate_required_string(data, 'name', min_len=1, max_len=100)
        if error is not None:
            return error

        # Validate description
        description, error = validate_optional_string(data, 'description', max_len=500)
        if error is not None:
            return error

        # Create group
        group = application.create_group(user_id, name, description)

        # Get creator user info
        creator = application.get_user_by_id(user_id)

        # Return group in the format specified by API spec
        return jsonify({
            "id": group.id,
            "name": group.name,
            "description": group.description,
            "createdBy": {
                "id": creator.id,
                "email": creator.email,
                "name": creator.name
            },
            "memberCount": group.member_count
        }), 201

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

    # check_same_thread=False is necessary to allow multiple
    # threads to access the database concurrently
    db_conn = sqlite3.connect('database/costsharing.db', check_same_thread=False)
    db_storage = DatabaseCostStorage(db_conn)

    return create_app(oauth_handler, CostSharing(db_storage))


# This is "main" for the local launch and can be tested directly
if __name__ == '__main__':  # pragma: no cover
    launch().run(debug=True, port=8000)
