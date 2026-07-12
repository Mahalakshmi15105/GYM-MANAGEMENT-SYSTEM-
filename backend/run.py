from app import create_app
import atexit

app = create_app()

# Initialize background scheduler with error handling
scheduler = None
try:
    from apscheduler.schedulers.background import BackgroundScheduler
    from app.scheduler import generate_all_notifications
    
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        func=generate_all_notifications,
        trigger='interval',
        minutes=1,
        id='notification_generator',
        name='Generate notifications every minute',
        replace_existing=True
    )
    
    # Shut down the scheduler when exiting the app
    atexit.register(lambda: scheduler.shutdown() if scheduler else None)
    
except ImportError as e:
    print(f"Warning: APScheduler not installed. Notification system will be disabled. Error: {e}")
except Exception as e:
    print(f"Warning: Failed to initialize notification scheduler. Error: {e}")

if __name__ == '__main__':
    # Start the scheduler if it was successfully initialized
    if scheduler:
        try:
            scheduler.start()
            print("Notification scheduler started successfully")
        except Exception as e:
            print(f"Error: Failed to start notification scheduler. Error: {e}")
            scheduler = None
    
    # Start Flask on port 5000
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
