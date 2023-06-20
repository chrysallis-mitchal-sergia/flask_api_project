from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from config import Config
import jwt

limiter = Limiter(key_func=get_remote_address)

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    limiter.init_app(app)

    # JWT Token Configuration
    app.secret_key = 'Secret'
    payload = {
        "sub": "111333",
        "name": "Shhhh",
        "iat": 1516239022
        }
    token = jwt.encode(payload, app.secret_key, algorithm="HS256")
    print(token)

    from service import hello
    app.register_blueprint(hello.bp)
    from service import clear_database
    app.register_blueprint(clear_database.bp)
    from service import store_lookup_data
    app.register_blueprint(store_lookup_data.bp)
    from service import report_abuse
    app.register_blueprint(report_abuse.bp)
    from service import all_records
    app.register_blueprint(all_records.bp)
    from service import lookup
    app.register_blueprint(lookup.bp)

    return app

if __name__ == '__main__':
    app = create_app()
    print('Server is running..')
    app.run(debug=True)