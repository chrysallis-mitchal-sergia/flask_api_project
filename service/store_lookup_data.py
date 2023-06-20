from flask import Blueprint
from flask import request, jsonify
from utils.redis_utils import get_redis
from utils.jwt_utils import token_required
import json

bp = Blueprint('store_lookup_data', __name__)

@bp.route('/store-lookup-data', methods=['POST'])
@token_required
# Add lookup data in the database
def store_lookup_data():
    redis_client = get_redis()
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

        return jsonify({'message': 'Data appended successfully'}, {'data': data}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500