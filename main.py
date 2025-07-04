from flask import Flask, render_template, request, jsonify, send_from_directory
import cv2
import os
import threading
import time
import logging

app = Flask(__name__, template_folder='templates', static_folder='static')

# ✅ Internal app storage (Android-safe)
app_root = os.path.expanduser("~")
known_faces_dir = os.path.join(app_root, "known_faces")
os.makedirs(known_faces_dir, exist_ok=True)

camera_index = 1  # Prefer front camera
cap = None

def init_camera():
    global cap
    logging.warning("Initializing front camera (index 1)...")
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        logging.warning("Front camera failed. Trying back camera (index 0)...")
        cap = cv2.VideoCapture(0)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/capture", methods=["GET"])
def capture_frame():
    if cap is None or not cap.isOpened():
        return jsonify({"error": "Camera not initialized"}), 500
    ret, frame = cap.read()
    if not ret:
        return jsonify({"error": "Failed to capture frame"}), 500
    filename = f"face_{int(time.time())}.jpg"
    path = os.path.join(known_faces_dir, filename)
    cv2.imwrite(path, frame)
    return jsonify({"status": "ok", "image": f"/faces/{filename}"})

@app.route("/faces/<path:filename>")
def serve_known_faces(filename):
    return send_from_directory(known_faces_dir, filename)

@app.route("/static/<path:filename>")
def serve_static(filename):
    return send_from_directory("static", filename)

if __name__ == "__main__":
    logging.warning("Starting Flask server on 0.0.0.0:5000...")
    init_camera()
    app.run(host="0.0.0.0", port=5000)
