import firebase_admin
from firebase_admin import credentials, auth
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Initialize Firebase Admin SDK
cred = credentials.Certificate('D:/College Work/Assignments, Projects & Extra/College Projects/Inkcode/mail-system/inkcode-cadec-firebase-adminsdk-m8ngo-4d5ebae0e7.json')
firebase_admin.initialize_app(cred)

# Set up the SMTP server for Gmail (use an app password if 2FA is enabled)
smtp_server = 'smtp.gmail.com'
smtp_port = 587
smtp_user = 'inkcode.com@gmail.com'  # Your Gmail address
smtp_pass = 'ahze avrz enqc ptfk'  # Your Gmail app-specific password

# Fetch all user emails from Firebase Authentication
def get_user_emails():
    user_emails = []
    
    page = auth.list_users()
    while page:
        for user in page.users:
            user_emails.append(user.email)
        if page.has_next_page:
            page = page.get_next_page()
        else:
            break
    return user_emails

# Send email to all users
def send_email_to_users(emails, subject, body):
    # Create message container
    msg = MIMEMultipart()
    msg['From'] = smtp_user
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    # Join all emails into a single comma-separated string for the 'To' header
    msg['To'] = ', '.join(emails)

    try:
        # Connect to the SMTP server and send emails
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Secure connection
        server.login(smtp_user, smtp_pass)

        # Send email to all users in one message
        server.sendmail(smtp_user, emails, msg.as_string())
        print(f"Email sent to {len(emails)} recipients.")

        server.quit()
        print("All emails sent successfully.")
    except Exception as e:
        print(f"Error sending email: {e}")

if __name__ == '__main__':
    users_emails = get_user_emails()
    email_subject = '🎉 Join the InkCode Community on GitHub Discussions! 🚀'
    email_body = '''
Hello!

We’re excited to announce that the InkCode Community is now live on GitHub Discussions! This new space is designed for you to connect with other InkCode users, share ideas, and get the support you need.

What’s happening in our GitHub Community?
Our GitHub Discussions will be a hub for:

Q&A: Ask questions about using InkCode and get help from fellow users and the InkCode team.
Feature Requests: Share ideas or features you’d like to see in InkCode.
Project Collaboration: Discover tips and discuss workflows that make collaborative coding better than ever.
General Discussions: Explore topics, offer feedback, and help shape the future of InkCode.
Ready to join?
Head over to our community on GitHub and introduce yourself! We’d love to know more about what you’re working on and what you hope to see in InkCode.

👉 Join the InkCode Community here: [GitHub Discussions Link]

Thank you for being a part of InkCode's journey. We’re looking forward to building an amazing, collaborative experience together.

Best,
The InkCode Team'''

    send_email_to_users(users_emails, email_subject, email_body)
