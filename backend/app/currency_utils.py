from app.models import Gym


DEFAULT_CURRENCY = 'INR'


def get_gym_currency(gym_id):
    """Get currency for a specific gym"""
    if not gym_id:
        return DEFAULT_CURRENCY
    
    gym = Gym.query.get(gym_id)
    if not gym or not gym.currency:
        return DEFAULT_CURRENCY
    
    return gym.currency.strip().upper()