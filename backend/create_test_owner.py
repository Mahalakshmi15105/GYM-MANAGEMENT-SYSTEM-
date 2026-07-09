
from app import create_app
from app.extensions import db, bcrypt
from app.models import User, Gym

app = create_app()
with app.app_context():
    # Create test gym
    gym = Gym(name="Test Gym X", address="456 Test Ave", phone="555-0456")
    db.session.add(gym)
    db.session.flush()
    
    # Create test user with known password
    hashed_password = bcrypt.generate_password_hash("testpass123").decode('utf-8')
    user = User(
        name="Test Owner X",
        email="testownerx@testgym.com",
        password_hash=hashed_password,
        role="gym_owner",
        gym_id=gym.id
    )
    db.session.add(user)
    db.session.commit()
    print(f"Created test gym owner! Email: testownerx@testgym.com, Password: testpass123, Gym ID: {gym.id}")
