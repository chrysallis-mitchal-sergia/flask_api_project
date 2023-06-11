# ================= Lib imports =================
try:
    from flask import Flask, request, jsonify
except ImportError:
    print("No module named 'flask' found")

try:
    import redis
except ImportError:
    print("No module named 'redis' found")

try:
    import json
except ImportError:
    print("No module named 'json' found")

try:
    import jwt
except ImportError:
    print("No module named 'jwt' found")

try:
    from functools import wraps
except ImportError:
    print("No module named 'wraps' found")

try:
    import os
except ImportError:
    print("No module named 'os' found")

try:
    import secrets
except ImportError:
    print("No module named 'secrets' found")

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# ===============================================
#Redis client
redis_client = redis.Redis(host='localhost', port=6379, db=0)

# Create a Flask app: Create a new Flask app by instantiating the `Flask` class:
app = Flask(__name__)
counter=0
limiter = Limiter(app)
limiter.key_func = get_remote_address
app.secret_key = 'AlchemySec'
payload = {
  "sub": "111333",
  "name": "Alchemy",
  "iat": 1516239022
}

token = jwt.encode(payload, app.secret_key, algorithm="HS256")
print(token)

# =========================================================
def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            token = auth_header.split(' ')[1]  # Assuming the token is in the format 'Bearer <token>'

        if not token:
            return jsonify({'message': 'a valid token is missing'}), 401
        try:
            data = jwt.decode(token, app.secret_key, algorithms=["HS256"])
        except jwt.InvalidTokenError:
            return jsonify({'message': 'token is invalid'}), 401

        return f(*args, **kwargs)

    return decorator

# =================== Endpoints mapping ===================
@app.route('/')
def hello():
    return 'Hello, World!'

@app.route('/clear_database', methods=['GET'])
@token_required
def clear_database():
    redis_client.flushdb()
    return 'Redis database cleared.'

@app.route('/report-abuse', methods=['POST'])
@token_required
# Create IP abuse records
def store_data():
    try:
        data = request.get_json()  # Assuming the request body contains a JSON payload

        # Check if the JSON payload is valid
        if not data:
            return jsonify({'error': 'Invalid JSON payload'}), 400

        counter = redis_client.incr('counter')  # Generate a unique key using Redis' INCR operation
        key = f'data:{counter}'

        # Store the JSON payload in Redis
        redis_client.set(key, json.dumps(data))

        # Create a secondary index mapping attribute value to key
        attribute_value = data.get('ipAddress')  # Change 'attribute' to the desired attribute name
        redis_client.sadd('index:' + attribute_value, key)

        counter += 1  # Increment the counter for the next entry

        return jsonify({'message': 'Data stored successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/all-abuse-records', methods=['GET'])
# GET all records
def get_all_data():
    try:
        counter = int(redis_client.get('counter') or 0)  # Get the current value of the counter
        data = []

        for i in range(1, counter + 1):
            key = f'data:{i}'
            json_data = redis_client.get(key)
            if json_data:
                data.append(json.loads(json_data))

        return jsonify({'data': data}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/ip-info/<attribute_value>', methods=['GET'])
#Fetch specified IP address data
@limiter.limit("5/minute")
def get_ip_data(attribute_value):
    # Retrieve keys from the secondary index
    try:
        keys = redis_client.smembers('index:' + attribute_value)  # Retrieve keys from the secondary index

        # Retrieve JSON entries based on keys
        data = []

        for key in keys:
            json_data = redis_client.get(key)
            if json_data:
                data.append(json.loads(json_data))

        return jsonify({'data': data}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500



if __name__ == '__main__':
    print('Server is running..')
    app.run(debug=True)