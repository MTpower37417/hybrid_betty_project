from flask import Flask

app = Flask(__name__)


@app.route('/')
def index():
    return "Betty AI is running!"


if __name__ == "__main__":
    print("Starting Betty AI server...")
    try:
        app.run(host='0.0.0.0', port=5000, debug=True)
    except Exception as e:
        print(f"Error starting server: {e}")
