
from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import cv2
import time
import logging
import numpy as np
import sys

# Enable logging to stderr for Android logcat visibility
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

app = Flask(__name__, template_folder='templates', static_folder='static')

# Android internal storage directory
app_root = os.path.expanduser("~")
known_faces_dir = os.path.join(app_root, "known_faces")
os.makedirs(known_faces_dir, exist_ok=True)

@app.route("/")
def home():
    logging.debug("Serving index.html")
    return render_template("index.html")

@app.route("/capture", methods=["GET"])
def capture_frame():
    logging.debug("Capture endpoint hit, initializing camera...")
    try:
        cap = cv2.VideoCapture(1)
        if not cap.isOpened():
            logging.warning("Front camera (1) failed, trying back camera (0)")
            cap = cv2.VideoCapture(0)

        if not cap.isOpened():
            logging.error("No camera could be opened.")
            return jsonify({"error": "Unable to access camera"}), 500

        ret, frame = cap.read()
        cap.release()

        if not ret:
            logging.error("Failed to capture frame")
            return jsonify({"error": "Failed to capture frame"}), 500

        filename = f"face_{int(time.time())}.jpg"
        path = os.path.join(known_faces_dir, filename)
        cv2.imwrite(path, frame)

        logging.info(f"Saved image to {path}")
        return jsonify({"status": "ok", "image": f"/faces/{filename}"})
    except Exception as e:
        logging.exception("Exception in capture_frame")
        return jsonify({"error": str(e)}), 500

@app.route("/faces/<path:filename>")
def serve_known_faces(filename):
    return send_from_directory(known_faces_dir, filename)

@app.route("/static/<path:filename>")
def serve_static(filename):
    return send_from_directory("static", filename)

if __name__ == "__main__":
    logging.warning("Starting Flask server on 0.0.0.0:5000")
    app.run(host="0.0.0.0", port=5000)
