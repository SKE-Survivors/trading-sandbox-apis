from flask import Flask
from flask_cors import CORS
from authlib.integrations.flask_client import OAuth
from loginpass import create_flask_blueprint, Google, GitHub
from decouple import config
from handler import handle_authorize
import config as conf
import api

app = Flask(__name__)
app.secret_key = conf.SECRET_KEY
app.config.from_pyfile('config.py')
CORS(app)

oauth = OAuth(app)
services = [Google, GitHub]  # add services here
oauth_endpoint = create_flask_blueprint(services, oauth, handle_authorize)

# /api/auth/login
app.register_blueprint(api.auth_endpoint, url_prefix='/api/auth')
# /api/auth/login/{service}
app.register_blueprint(oauth_endpoint, url_prefix='/api/auth')

app.register_blueprint(api.trading_endpoint, url_prefix='/api/trading')
app.register_blueprint(api.info_endpoint, url_prefix='/api/info')
app.register_blueprint(api.service_endpoint, url_prefix='/api/service')


@app.route('/')
def root():
    return 'all good!'


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=config("PORT"), debug=False)
