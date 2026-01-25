from flask import Flask, jsonify

app = Flask(__name__)


@app.route("/")
def server_info():
    return "My server"


@app.route("/author")
def author():
    author = {
        "name": "Katya",
        "course": 2,
        "age": 18,
    }
    return jsonify(author)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
