from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from datetime import timedelta
from global_util import log_util
from login import *
from home import *
from create import *
from check import *
from annualLeaveSummary import *

# Set up loggin place
log_util.log_init()

# The main flask
app = Flask(__name__)
jwt = JWTManager()
CORS(app)
app.config['JWT_SECRET_KEY'] = 'temp_secrete_key'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=30)  # Token expires in 30 minutes
jwt.init_app(app)

app.register_blueprint(loginApp)
app.register_blueprint(homeApp)
app.register_blueprint(createApp)
app.register_blueprint(checkApp)
app.register_blueprint(annual_leave_summaryApp)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
