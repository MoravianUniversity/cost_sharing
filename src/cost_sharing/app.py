from flask import Flask

def create_app():
    app = Flask(__name__)

    @app.route('/')
    def index():
        return "Hello, World!"

    return app


# This is "main" for the gunicorn launch and cannot be tested directly
def launch():  # pragma: no cover
    return create_app()


# This is "main" for the local launch and can be tested directly
if __name__ == '__main__':  # pragma: no cover
    launch().run(debug=True, port=8000)

