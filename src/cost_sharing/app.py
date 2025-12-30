from flask import Flask

def create_app():
    app = Flask(__name__)

    @app.route('/')
    def index():
        return "Hello, World!"

    return app

def launch():
    return create_app()


def main():
    app = create_app()
    app.run(debug=True, port=8000)


if __name__ == '__main__':
    main()
