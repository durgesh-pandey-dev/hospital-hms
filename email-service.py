from flask import Flask, request, jsonify
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)

import os
GMAIL_USER = os.environ.get('GMAIL_USER', '')
GMAIL_PASSWORD = os.environ.get('GMAIL_PASSWORD', '')

@app.route('/send-email', methods=['POST'])
def send_email():
    try:
        data = request.json
        trigger = data.get('trigger')
        to_email = data.get('email')

        templates = {
            'SIGNUP_WELCOME': {
                'subject': 'Welcome to HMS!',
                'body': f"Hello {data.get('name', 'User')},\n\nWelcome to Hospital Management System!\n\nRegards,\nHMS Team"
            },
            'BOOKING_CONFIRMATION': {
                'subject': 'Appointment Confirmed!',
                'body': f"Hello,\n\nYour appointment with Dr. {data.get('doctor_name')} on {data.get('date')} at {data.get('time')} is confirmed.\n\nRegards,\nHMS Team"
            }
        }

        template = templates.get(trigger)
        if not template:
            return jsonify({'error': 'Invalid trigger'}), 400

        msg = MIMEMultipart()
        msg['From'] = GMAIL_USER
        msg['To'] = to_email
        msg['Subject'] = template['subject']
        msg.attach(MIMEText(template['body'], 'plain'))

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(GMAIL_USER, GMAIL_PASSWORD)
            server.send_message(msg)

        return jsonify({'message': 'Email sent successfully'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(port=3000, debug=True)