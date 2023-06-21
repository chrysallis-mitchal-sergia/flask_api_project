from flask import Blueprint, jsonify
from flask import request
from utils.redis_utils import get_redis
import json

bp = Blueprint('lookup', __name__)

@bp.route('/lookup', methods=['GET'])
#Fetch specified IP address data
def get_ip_data():
    # Retrieve keys from the secondary index
    redis_client = get_redis()
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

            # Pagination
            page = int(request.args.get('page', 1))
            page_size = int(request.args.get('page_size', 10))
            start_index = (page - 1) * page_size
            end_index = start_index + page_size
            paginated_data = data[start_index:end_index]

            return jsonify({'data': paginated_data}), 200

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

            # Pagination
            page = int(request.args.get('page', 1))
            page_size = int(request.args.get('page_size', 10))
            start_index = (page - 1) * page_size
            end_index = start_index + page_size
            paginated_data = data[start_index:end_index]

            return jsonify({'data': paginated_data}), 200


    except Exception as e:
        return jsonify({'error': str(e)}), 500