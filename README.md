# Women-s-Safety-Application
A basic Women safety application which will have Timmer to set for bot audio and video recording.
Women Safety Mobile Flask Application

Overview

This project is a mobile Flask application designed for women's safety. The application provides features like sending emergency emails, recording audio and video, and managing timers for both recording and countdown functionalities. It aims to provide a simple and efficient way to assist users in emergency situations.

Features

Manual Email Setup: Users can manually input their email and password for sending emergency emails.

Emergency Email Entry: Allows users to specify emergency email addresses where recordings will be sent.

Timer Functionality:

Countdown timer before recording starts.

Recording timer to manage the duration of audio or video recording.

Audio and Video Recording:

Record audio-only or audio with video based on user preference.

Save recordings locally for email attachment.

Deactivation Button: Stop the recording at any time.

Email Sending: Automatically send recordings to specified emergency email addresses.

Prerequisites

Python 3.7+

Flask

Dependencies for audio and video recording:

sounddevice

wavio

opencv-python

Email account credentials (e.g., Gmail) to send emergency emails.

Installation

Clone the Repository:

git clone <repository_url>
cd women_safety_app

Install Dependencies:

pip install -r requirements.txt

Set Environment Variables:
Create a .env file to store your Flask environment variables.

FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your_secret_key

Run the Application:

flask run

Open the application in your mobile browser or use a mobile-friendly interface.

Usage

Setup Timer and Recording Mode:

Select the countdown timer duration.

Choose the recording mode (audio-only or audio with video).

Input Details:

Enter your email credentials and emergency email addresses.

Start Timer:

Wait for the countdown timer to complete.

Recording Begins:

Audio and/or video recording starts automatically.

Deactivation:

Stop the recording manually if required.

Automatic Email Sending:

Recordings are automatically sent to the emergency email addresses.

File Structure

.
├── app.py                # Main Flask application
├── templates/            # HTML templates for the UI
├── static/               # Static files (CSS, JS)
├── recordings/           # Directory for saved recordings
├── requirements.txt      # Python dependencies
└── README.md             # Project documentation

Troubleshooting

Common Issues

Video Recording Not Working:

Ensure your camera is accessible by the application.

Check if opencv-python is installed.

Email Sending Fails:

Verify your email credentials.

Enable access for less secure apps if using Gmail.

Future Enhancements

Real-Time Location Sharing: Add functionality to send the user’s real-time location with emails.

Push Notifications: Notify emergency contacts when a recording starts.

Cloud Integration: Save recordings in a secure cloud storage.

License

This project is licensed under the MIT License.

Contributing

Contributions are welcome! Please fork this repository, make changes, and submit a pull request.

Contact

For any inquiries or issues, please contact [nagulakondakarthikeya@gmail.com].
