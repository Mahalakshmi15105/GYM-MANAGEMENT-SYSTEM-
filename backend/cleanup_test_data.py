from app import create_app
from app.extensions import db
from app.models import Gym, User

app = create_app()
with app.app_context():
    test_user = User.query.filter_by(email='test@example.com').first()
    if test_user:
        db.session.delete(test_user)
    gym = Gym.query.filter_by(name='Test Gym').first()
    if gym:
        db.session.delete(gym)
    db.session.commit()
    print('Test data cleaned up')
