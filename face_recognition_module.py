# Face recognition disabled due to tensorflow conflicts
# All other JARVIS features work perfectly!

def register_face(name):
    return "Face recognition is currently unavailable sir. All other systems are fully operational."

def start_face_recognition(speak_fn):
    print("⚠️ Face recognition disabled — all other features working!")

def stop_face_recognition():
    pass

def is_face_command(user_input):
    keywords = ["register my face", "face recognition", "remember my face"]
    return any(k in user_input.lower() for k in keywords)

def handle_face_command(user_input, user_name=None):
    return "Face recognition is currently unavailable sir. All other systems are fully operational."

def get_known_faces():
    return []