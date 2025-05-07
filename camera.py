import cv2
import mediapipe as mp
import numpy as np
import serial
import time
import os
from collections import deque
from datetime import datetime

# === Serial Setup ===
arduino = serial.Serial('COM7', 9600)   # Servo Arduino
receiver = serial.Serial('COM6', 9600)  # Trigger Arduino
time.sleep(2)

# === MediaPipe Setup ===
mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils

face_mesh = mp_face_mesh.FaceMesh(
    static_image_mode=False,
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# === Camera Setup ===
cap = cv2.VideoCapture(0)

# === Parameters
x_deadzone_large = 5
x_deadzone_small = 2
y_deadzone_large = 5
y_deadzone_small = 2
last_x_sent = 90
last_y_sent = 90
CENTERED = False
centered_start_time = None
screenshot_taken = False

# === Screenshot directory
screenshots_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "screenshots")
os.makedirs(screenshots_dir, exist_ok=True)

# === Moving average smoothing
x_history = deque(maxlen=10)
y_history = deque(maxlen=10)

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        continue

    h, w, _ = frame.shape
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb_frame)

    annotated_frame = frame.copy()

    # === Dynamic Center Box
    box_width = int(w * 0.2)
    box_height = int(h * 0.2)
    x_center_min = w // 2 - box_width // 2
    x_center_max = w // 2 + box_width // 2
    y_center_min = h // 2 - box_height // 2
    y_center_max = h // 2 + box_height // 2

    if results.multi_face_landmarks:
        face_landmarks = results.multi_face_landmarks[0]

        mp_drawing.draw_landmarks(
            annotated_frame, face_landmarks, mp_face_mesh.FACEMESH_TESSELATION,
            landmark_drawing_spec=None,
            connection_drawing_spec=mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=1, circle_radius=1)
        )

        nose_tip = face_landmarks.landmark[4]
        nose_x = int(nose_tip.x * w)
        nose_y = int(nose_tip.y * h)

        x_history.append(nose_x)
        y_history.append(nose_y)

        smoothed_x = int(np.mean(x_history))
        smoothed_y = int(np.mean(y_history))

        print(f"[Nose] x: {smoothed_x}, y: {smoothed_y}")

        is_centered = (x_center_min <= smoothed_x <= x_center_max and
                       y_center_min <= smoothed_y <= y_center_max)

        # === Servo X movement
        angle_x = int(np.interp(smoothed_x, [0, w], [0, 180]))
        angle_x = max(0, min(angle_x, 180))
        diff_x = abs(angle_x - last_x_sent)

        if diff_x > x_deadzone_large:
            arduino.write(f"X:{angle_x}\n".encode('utf-8'))
            print(f"[MOVE X] → angle: {angle_x}")
            last_x_sent = angle_x
            time.sleep(0.3)
        elif diff_x > x_deadzone_small:
            arduino.write(f"X:{angle_x}\n".encode('utf-8'))
            print(f"[NUDGE X] → angle: {angle_x}")
            last_x_sent = angle_x
            time.sleep(0.1)

        # === Servo Y movement
        angle_y = int(np.interp(smoothed_y, [0, h], [0, 180]))
        angle_y = max(0, min(angle_y, 180))
        diff_y = abs(angle_y - last_y_sent)

        if diff_y > y_deadzone_large:
            arduino.write(f"Y:{angle_y}\n".encode('utf-8'))
            print(f"[MOVE Y] → angle: {angle_y}")
            last_y_sent = angle_y
            time.sleep(0.3)
        elif diff_y > y_deadzone_small:
            arduino.write(f"Y:{angle_y}\n".encode('utf-8'))
            print(f"[NUDGE Y] → angle: {angle_y}")
            last_y_sent = angle_y
            time.sleep(0.1)

        # === Centered logic for screenshot and trigger
        if is_centered:
            if not CENTERED:
                CENTERED = True
                centered_start_time = time.time()
                print("[CENTERED] Starting timer")
            else:
                centered_duration = time.time() - centered_start_time
                cv2.putText(annotated_frame, f"Centered for: {centered_duration:.1f}s",
                            (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

                if centered_duration >= 2.0 and not screenshot_taken:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"face_centered_{timestamp}.jpg"
                    path = os.path.join(screenshots_dir, filename)
                    success = cv2.imwrite(path, frame)
                    if success:
                        print(f"[SCREENSHOT] Saved: {path}")
                        screenshot_taken = True
                        cv2.putText(annotated_frame, "Screenshot Taken!",
                                    (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                        try:
                            receiver.write(b"go\n")
                            time.sleep(4)
                            print("[TRIGGER] Sent 'go' to COM6")
                        except Exception as e:
                            print(f"[ERROR] Failed to trigger COM6: {e}")
        else:
            CENTERED = False
            centered_start_time = None
            screenshot_taken = False

    else:
        print("[INFO] No face detected")
        CENTERED = False
        centered_start_time = None
        screenshot_taken = False

    # === Draw center box
    cv2.rectangle(annotated_frame, (x_center_min, y_center_min), (x_center_max, y_center_max), (255, 0, 0), 2)
    cv2.putText(annotated_frame, "Centered Zone",
                (x_center_min, y_center_min - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
    cv2.putText(annotated_frame, f"X:{x_center_min}-{x_center_max}, Y:{y_center_min}-{y_center_max}",
                (x_center_min, y_center_max + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)

    # === Display
    cv2.imshow("Lebron Cam", annotated_frame)

    if cv2.waitKey(5) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
arduino.close()
receiver.close()
