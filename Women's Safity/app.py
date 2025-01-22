from flask import Flask, render_template, request, jsonify
import sounddevice as sd
import wavio
import cv2
import time
import threading
import os
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from email.mime.text import MIMEText
from concurrent.futures import ThreadPoolExecutor
import requests

app = Flask(__name__)

# Ensure the recordings folder exists
audio_folder = 'recordings'
video_folder = 'videos'
if not os.path.exists(audio_folder):
    os.makedirs(audio_folder)
if not os.path.exists(video_folder):
    os.makedirs(video_folder)

# Global variables
stop_recording = False
is_recording = False  # Track if recording is in progress
recording_lock = threading.Lock()  # Lock to prevent concurrent recordings
record_video = False  # Default video recording toggle


def record_audio(duration=60):  # Default duration to 60 seconds
    global stop_recording
    fs = 44100  # Sample rate
    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"recording_{current_time}.wav"
    audio_file_path = os.path.join(audio_folder, filename)

    print(f"Recording audio for {duration} seconds...")

    with recording_lock:  # Acquire the lock
        recording = sd.rec(int(duration * fs), samplerate=fs, channels=2)
        sd.wait()  # Wait until recording is finished

        if stop_recording:
            print("Audio recording was stopped.")
            return None  # If stopped before finish

        wavio.write(audio_file_path, recording, fs, sampwidth=2)
        print("Audio recording finished and saved as:", audio_file_path)
        return audio_file_path


def record_video_file(duration=60, enable_recording="yes"):
    global stop_recording

    # Check if recording is enabled
    if enable_recording.lower() == "OFF":
        print("Video recording is disabled.")
        return None

    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    video_file_path = os.path.join(video_folder, f"video_{current_time}.avi")

    cap = cv2.VideoCapture(0)  # Start capturing video from the webcam
    if not cap.isOpened():
        print("Could not open webcam for video recording.")
        return None

    # Get the default video dimensions
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    out = cv2.VideoWriter(video_file_path, cv2.VideoWriter_fourcc(*'XVID'), 20.0, (frame_width, frame_height))

    start_time = time.time()
    print(f"Recording video for {duration} seconds...")
    while time.time() - start_time < duration:
        if stop_recording:
            print("Video recording was stopped.")
            break
        ret, frame = cap.read()
        if ret:
            out.write(frame)
        else:
            print("Error reading video frame.")
            break

    cap.release()
    out.release()
    print("Video recording finished and saved as:", video_file_path)
    return video_file_path if not stop_recording else None



# Function to get location details
def get_location_details():
    response = requests.get('https://ipinfo.io/json')
    data = response.json()
    return {
        'ip': data['ip'],
        'city': data['city'],
        'region': data['region'],
        'country': data['country'],
        'location': data['loc']
    }


# Function to send a single email
def send_single_email(user_email, user_password, to_email, audio_file, video_file=None):
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(user_email, user_password)

        # Get location details
        location_info = get_location_details()

        # Setup the MIME
        msg = MIMEMultipart()
        msg['From'] = user_email
        msg['To'] = to_email
        msg['Subject'] = 'Emergency Recording File with Location Details'

        # Email body
        body = f"""
        Emergency recording has been made.
        Location details:
        IP: {location_info['ip']}
        City: {location_info['city']}
        Region: {location_info['region']}
        Country: {location_info['country']}
        Location: {location_info['location']} (latitude, longitude)
        """
        msg.attach(MIMEText(body, 'plain'))

        # Attach the audio file
        if audio_file:
            with open(audio_file, 'rb') as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename={os.path.basename(audio_file)}'
                )
                msg.attach(part)

        # Attach the video file (if available)
        if video_file:
            with open(video_file, 'rb') as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename={os.path.basename(video_file)}'
                )
                msg.attach(part)

        # Send the email
        server.sendmail(user_email, to_email, msg.as_string())
        server.quit()

        print(f"Email sent to {to_email} with recording attached.")
        return f"Email sent to {to_email}"

    except Exception as e:
        print(f"Failed to send email to {to_email}: {e}")
        return f"Failed to send email to {to_email}: {str(e)}"


def send_email(user_email, user_password, to_emails, audio_file, video_file=None):
    with ThreadPoolExecutor(max_workers=5) as executor:  # Adjust max_workers for concurrency
        futures = [executor.submit(send_single_email, user_email, user_password, to_email, audio_file, video_file)
                   for to_email in to_emails]
        results = [future.result() for future in futures]

    return results


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/set_timer', methods=['POST'])
def set_timer():
    global stop_recording, is_recording, record_video
    if is_recording:
        return jsonify({"message": "Recording is already in progress. Please deactivate before starting a new one."}), 400

    stop_recording = False  # Reset stop recording flag
    is_recording = True  # Set to true when starting recording

    data = request.get_json()
    timer_minutes = int(data['time'])
    timer_seconds = timer_minutes * 60
    user_email = data['user_email']
    user_password = data['user_password']
    emergency_emails = [email.strip() for email in data['emergency_email'].split(',')]
    recording_duration_minutes = int(data['recording_duration'])  # Get the recording duration in minutes
    recording_duration_seconds = recording_duration_minutes * 60  # Convert to seconds
    record_video = data.get('record_video', 'false').lower() == 'true'  # Ensure this is correctly passed and checked

    def start_recording():
        time.sleep(timer_seconds)  # Wait for the timer to finish
        audio_file = record_audio(duration=recording_duration_seconds)  # Record audio
        video_file = None

        if record_video:  # Record video if video recording is enabled
            video_file = record_video_file(duration=recording_duration_seconds, enable_recording="ON")
        else:  # Only audio recording if video is disabled
            video_file = None  # No video recording

        if audio_file or video_file:
            # Send emails in parallel
            email_status_list = send_email(user_email, user_password, emergency_emails, audio_file, video_file)
            for email_status in email_status_list:
                print(email_status)

        # Reset the recording state
        global is_recording
        is_recording = False

    threading.Thread(target=start_recording).start()
    return jsonify({"message": f"Timer set for {timer_minutes} minute(s). Recording will start when the timer finishes."})



@app.route('/deactivate', methods=['POST'])
def deactivate():
    global stop_recording
    stop_recording = True  # Stop the recording
    return jsonify({"message": "Recording deactivated."})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
