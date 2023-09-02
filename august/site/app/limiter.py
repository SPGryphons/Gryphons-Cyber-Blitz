from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# This is the limiter for account creation
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["5 per second"]
)