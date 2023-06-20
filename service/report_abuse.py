from flask import Blueprint
from flask import request, jsonify
from utils.redis_utils import get_redis
from utils.jwt_utils import token_required
import json

bp = Blueprint('report_abuse', __name__)

@bp.route('/report-abuse', methods=['POST'])
@token_required
# Report IP abuse data
def report_abuse():
    redis_client = get_redis()
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