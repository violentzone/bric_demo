from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from login import *
from home import *

app = Flask(__name__)
jwt = JWTManager()
CORS(app)
app.config['JWT_SECRET_KEY'] = 'temp_secrete_key'
jwt.init_app(app)

app.register_blueprint(loginApp)
app.register_blueprint(homeApp)



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
