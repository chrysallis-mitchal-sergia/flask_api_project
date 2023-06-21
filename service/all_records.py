from flask import Blueprint, jsonify, request
from utils.redis_utils import get_redis
import json

bp = Blueprint('all_records', __name__)

@bp.route('/all-records', methods=['GET'])
# GET all records
def get_all_data():
    redis_client = get_redis()
    try:
        counter = int(redis_client.get('counter') or 0)  # Get the current value of the counter
        page = int(request.args.get('page', 1))  # Get the page number from the query parameters
        page_size = int(request.args.get('page_size', 10))  # Get the page size from the query parameters
        start_index = (page - 1) * page_size
        end_index = start_index + page_size

        data = []

        for i in range(start_index + 1, end_index + 1):
            key = f'data:{i}'
            json_data = redis_client.get(key)
            if json_data:
                data.append(json.loads(json_data))

        return jsonify({'data': data}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500