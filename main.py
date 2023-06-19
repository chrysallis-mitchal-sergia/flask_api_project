# ================= Lib imports =================
from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import redis
import json
import jwt
from functools import wraps

# ===============================================
#Redis client
redis_client = redis.Redis(host='localhost', port=6379, db=0)

# Create a Flask app: Create a new Flask app by instantiating the `Flask` class:
app = Flask(__name__)

counter=0

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "5 per minute"],
    storage_uri="memory://",
)

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
    return 'Goo!'

@app.route('/clear-database', methods=['POST'])
@token_required
def clear_database():
    redis_client.flushdb()
    return 'Redis database cleared.'

@app.route('/add-lookup-data', methods=['POST'])
@token_required
# Add lookup data in the database
def store_lookup_data():
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
        attribute_value = data.get('ipAddress')
        redis_client.sadd('index:' + attribute_value, key)

        counter += 1  # Increment the counter for the next entry

        return jsonify({'message': 'Data stored successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/report-abuse', methods=['POST'])
@token_required
# Report IP abuse data
def report_abuse():
    try:
        data = request.get_json()  # Assuming the request body contains a JSON payload

        # Check if the JSON payload is valid
        if not data:
            return jsonify({'error': 'Invalid JSON payload'}), 400

        ip_address = data.get('ipAddress')
        if not ip_address:
            return jsonify({'error': 'Missing ipAddress attribute'}), 400

        # Get the keys associated with the provided ipAddress
        keys = redis_client.smembers('index:' + ip_address)

        # Check if any keys exist for the provided ipAddress
        if not keys:
            return jsonify({'error': 'No data found for the provided ipAddress'}), 404

        # Iterate over the keys and append the new attributes to the JSON payload
        for key in keys:
            stored_data = redis_client.get(key)
            if stored_data:
                stored_data = json.loads(stored_data)
                stored_data.update(data)
                redis_client.set(key, json.dumps(stored_data))

        return jsonify({'message': 'Data appended successfully'}, {'data': stored_data}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/all-records', methods=['GET'])
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

@app.route('/lookup', methods=['GET'])
#Fetch specified IP address data
@limiter.limit("10/minute", override_defaults=True)
def get_ip_data():
    # Retrieve keys from the secondary index
    try:
        ip_address = request.args.get('ipAddress')
        abuse_category = request.args.get('abuseCategory')

        if not ip_address and not abuse_category:
            return jsonify({'error': 'No URL parameter provided'}), 400
        elif ip_address:
            keys = redis_client.smembers('index:' + ip_address)  # Retrieve keys from the secondary index
            # Retrieve JSON entries based on keys
            data = []
            for key in keys:
                json_data = redis_client.get(key)
                if json_data:
                    data.append(json.loads(json_data))
            return jsonify({'data': data}), 200

        elif abuse_category:
            keys = redis_client.keys('data:*')
            # Retrieve JSON entries based on keys
            data = []
            for key in keys:
                stored_data = redis_client.get(key)
                if stored_data:
                    stored_data = json.loads(stored_data)
                if int(abuse_category) in stored_data.get('abuseCategories', []):
                    data.append(stored_data)
            return jsonify({'data': data}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print('Server is running..')
    app.run(debug=True)