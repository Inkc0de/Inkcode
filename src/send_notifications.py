import firebase_admin
from firebase_admin import credentials, firestore, auth
from datetime import datetime

# Initialize Firebase Admin SDK
cred = credentials.Certificate('D:\\College Work\\Assignments, Projects & Extra\\College Projects\\Inkcode\\src\\inkcode-cadec-firebase-adminsdk-m8ngo-4d5ebae0e7.json')
firebase_admin.initialize_app(cred)

# Firestore Client
db = firestore.client()

def send_notification_to_all_users(message):
    # Get all users from Firebase Authentication
    users = auth.list_users()
    
    for user in users.iterate_all():
        user_email = user.email
        user_id = user.uid
        
        notification_data = {
            'userId': user_id,
            'userEmail': user_email,
            'message': message,
            'timestamp': datetime.now(),
            'readStatus': False
        }
        
        # Add notification to Firestore
        db.collection('notifications').add(notification_data)
        print(f"Notification sent to {user_email}")

if __name__ == "__main__":
    message = '''
    
Hello !

    '''
    send_notification_to_all_users(message)
