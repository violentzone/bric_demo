from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from login import *
from home import *
from create import *
from check import *

app = Flask(__name__)
jwt = JWTManager()
CORS(app)
app.config['JWT_SECRET_KEY'] = 'temp_secrete_key'
jwt.init_app(app)

app.register_blueprint(loginApp)
app.register_blueprint(homeApp)
app.register_blueprint(createApp)
app.register_blueprint(checkApp)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
