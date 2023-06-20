from flask import Blueprint, jsonify
from utils.redis_utils import get_redis
import json

bp = Blueprint('all_records', __name__)

@bp.route('/all-records', methods=['GET'])
# GET all records
def get_all_data():
    redis_client = get_redis()
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