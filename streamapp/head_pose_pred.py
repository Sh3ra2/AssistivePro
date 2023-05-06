import cv2
import mediapipe as mp
import time
from .models import settings_model
# Initialize MediaPipe Face Mesh and Drawing utilities
mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils
face_mesh = mp_face_mesh.FaceMesh()

countL = 0
countR = 0
def detect_head_turns(frame, left_count, right_count, state, start_time, angle_f):

    req_count_time = settings_model.objects.get(id_settings = 1).head_count_time_sec
    left_move = settings_model.objects.get(id_settings = 1).left_head_threshHold
    right_move = settings_model.objects.get(id_settings = 1).right_head_threshHold
    # print("req data is", req_count_time)

    # Function to calculate face direction
    def estimate_face_direction(landmarks):
        nose_tip = landmarks[4]
        chin = landmarks[152]
        left_eye = landmarks[33]
        right_eye = landmarks[263]

        x_diff = right_eye.x - left_eye.x
        y_diff = right_eye.y - left_eye.y

        if x_diff == 0:
            angle = 90 if y_diff > 0 else -90
        else:
            angle = -1 * (180 / 3.14159265359) * (y_diff / x_diff)

        return angle

    # Function to label head pose based on the angle
    def label_head_pose(angle, left_threshold = left_move, right_threshold = right_move):
        
        if angle < left_threshold:
            return "Right"
        elif angle > right_threshold:
            return "Left"
        else:   
            return "Center"
    # print("angle f right after function ", angle_f)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Process the frame and get landmarks
    result = face_mesh.process(rgb_frame)

    if result.multi_face_landmarks:
        for face_landmarks in result.multi_face_landmarks:
            # Draw facial landmarks
            mp_drawing.draw_landmarks(frame, face_landmarks, mp_face_mesh.FACEMESH_TESSELATION)

            # Estimate face direction
            face_direction = estimate_face_direction(face_landmarks.landmark)
            angle_f = face_direction
            head_pose_label = label_head_pose(face_direction)

            # Update counters and state
            if state == "Center":
                if head_pose_label == "Left":
                    left_count += 1
                    state = "Left"
                elif head_pose_label == "Right":
                    right_count += 1
                    state = "Right"
            elif state != head_pose_label:
                state = head_pose_label

        # Reset counts after  seconds
        current_time = time.time()
        if current_time - start_time >= req_count_time:
            left_count = 0
            right_count = 0
            start_time = time.time()
            # print("Conter restarted after time limit")
    print("angle after function is  ",angle_f)
    return left_count, right_count, state, start_time, frame, angle_f
