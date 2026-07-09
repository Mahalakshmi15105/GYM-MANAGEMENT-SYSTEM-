
from app import create_app
from app.extensions import db
from app.models import User, Gym

app = create_app()
with app.app_context():
    users = User.query.all()
    print("Users in database:")
    for user in users:
        print(f"  ID: {user.id}, Name: {user.name}, Email: {user.email}, Role: {user.role}, Gym ID: {user.gym_id}")
        
    gyms = Gym.query.all()
    print("\nGyms in database:")
    for gym in gyms:
        print(f"  ID: {gym.id}, Name: {gym.name}, Logo: {gym.logo}")
