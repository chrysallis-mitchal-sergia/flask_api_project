from flask import Blueprint
from utils.jwt_utils import token_required
from utils.redis_utils import get_redis

bp = Blueprint('clear_database', __name__)

@bp.route('/clear-database', methods=['POST'])
@token_required
def clear_database():
    redis_client = get_redis()
    redis_client.flushdb()
    return 'Redis database cleared.'