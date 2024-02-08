from flask import Flask, request, jsonify
from flask_cors import CORS


app = Flask(__name__)
CORS(app)

@app.route('/login', methods=['POST'])
def login():
    print(request.json)
    return 'OK'

if __name__ == '__main__':
    app.run(host='0.0.0.0')