from app import create_app
from app.extensions import db
from app.models import Gym
import qrcode
from io import BytesIO

app = create_app()

with app.app_context():
    # Get a gym with QR code
    gym = Gym.query.first()
    if not gym:
        print("No gym found in database")
    else:
        print(f"Testing QR generation for gym: {gym.name}")
        print(f"QR Code: {gym.attendance_qr}")
        
        if not gym.attendance_qr:
            print("Gym has no QR code, generating one...")
            import uuid
            gym.attendance_qr = f"GYM{str(uuid.uuid4())[:12].upper()}"
            db.session.commit()
            print(f"Generated QR: {gym.attendance_qr}")
        
        try:
            # Generate QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(gym.attendance_qr)
            qr.make(fit=True)
            
            # Create QR image
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Save to BytesIO
            img_io = BytesIO()
            img.save(img_io, 'PNG')
            img_io.seek(0)
            
            print(f"QR image generated successfully")
            print(f"Image size: {len(img_io.getvalue())} bytes")
            
            # Save to file for verification
            with open('test_qr.png', 'wb') as f:
                f.write(img_io.getvalue())
            print("Saved to test_qr.png for visual verification")
            
        except Exception as e:
            print(f"Error generating QR: {e}")
            import traceback
            traceback.print_exc()
