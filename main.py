import cv2
import gradio as gr
import numpy as np
from contextlib import redirect_stdout
import io
import sys
import platform

# Global variables
camera = None
is_running = False
last_frame = None
error_message = None

# Initialize with a starting frame
last_frame = np.zeros((480, 640, 3), dtype=np.uint8)
cv2.putText(last_frame, "Press 'Start Webcam' to begin", (50, 240), 
           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

def create_error_image(error_text):
    """Create an error image with the error message"""
    img = np.zeros((480, 640, 3), dtype=np.uint8)
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.7
    color = (255, 255, 255)  # White text
    thickness = 1
    
    # Split text into lines
    y = 50
    for i, line in enumerate(error_text.split('\n')):
        if i > 6:  # Don't show more than 7 lines
            break
        cv2.putText(img, line, (20, y), font, font_scale, color, thickness, cv2.LINE_AA)
        y += 40
    
    return img

def initialize_camera():
    """Initialize the camera with optimized settings and detailed error reporting"""
    global camera, error_message
    
    try:
        print("Attempting to initialize camera...")
        
        if camera is None:
            # Try different camera indices
            for camera_index in [0, 1, 2]:
                print(f"Trying camera index {camera_index}...")
                # Handle Windows-specific backend
                if platform.system() == "Windows":
                    test_camera = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
                else:
                    test_camera = cv2.VideoCapture(camera_index)
                
                if test_camera.isOpened():
                    # Test if we can actually read from the camera
                    ret, frame = test_camera.read()
                    if ret and frame is not None:
                        camera = test_camera
                        print(f"Successfully initialized camera at index {camera_index}")
                        
                        # Optimize camera settings
                        camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                        camera.set(cv2.CAP_PROP_FPS, 30)
                        camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                        
                        error_message = None
                        return True
                    else:
                        print(f"Camera {camera_index} opened but cannot read frames")
                        test_camera.release()
                else:
                    print(f"Cannot open camera {camera_index}")
                    test_camera.release()
            
            # If we get here, no camera worked
            error_message = "No working camera found. Possible issues:\n" \
                          "1. Camera is being used by another application\n" \
                          "2. Camera drivers not installed\n" \
                          "3. Camera permissions denied\n" \
                          "4. No camera connected"
            print(error_message)
            return False
            
    except Exception as e:
        error_message = f"Camera initialization error: {str(e)}"
        print(error_message)
        return False
    
    return camera is not None and camera.isOpened()

def start_webcam():
    """Start the webcam feed with detailed error reporting"""
    global is_running, last_frame, error_message
    
    print("Starting webcam...")
    is_running = True
    
    if not initialize_camera():
        print(f"Failed to initialize camera: {error_message}")
        # Return an error image
        error_img = create_error_image(error_message or "Camera initialization failed")
        return error_img
    
    try:
        ret, frame = camera.read()
        if ret and frame is not None:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            last_frame = frame
            print("Webcam started successfully!")
            return frame
        else:
            error_msg = "Camera opened but cannot read frames"
            print(error_msg)
            error_img = create_error_image(error_msg)
            return error_img
            
    except Exception as e:
        error_msg = f"Error reading from camera: {str(e)}"
        print(error_msg)
        error_img = create_error_image(error_msg)
        return error_img

def stop_webcam():
    """Stop the webcam feed"""
    global is_running, camera
    
    print("Stopping webcam...")
    is_running = False
    
    if camera is not None:
        try:
            camera.release()
            print("Camera released successfully")
        except Exception as e:
            print(f"Error releasing camera: {e}")
        finally:
            camera = None
    
    return last_frame  # Return last frame instead of None

def get_webcam_frame():
    """Get current webcam frame with error handling"""
    global camera, is_running, last_frame, error_message
    
    if not is_running:
        return last_frame
    
    if camera is None:
        error_img = create_error_image("Camera not initialized")
        return error_img
    
    try:
        # Skip buffered frames to reduce lag
        if camera.get(cv2.CAP_PROP_BUFFERSIZE) > 1:
            for _ in range(int(camera.get(cv2.CAP_PROP_BUFFERSIZE)) - 1):
                camera.read()
        
        ret, frame = camera.read()
        if ret and frame is not None:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            last_frame = frame
            return frame
        else:
            error_img = create_error_image("Failed to read frame from camera")
            return error_img
            
    except Exception as e:
        error_msg = f"Error getting webcam frame: {str(e)}"
        print(error_msg)
        error_img = create_error_image(error_msg)
        return error_img

def check_camera_permissions():
    """Check if camera permissions are available"""
    try:
        # Try to list available cameras
        available_cameras = []
        for i in range(3):  # Check first 3 camera indices
            if platform.system() == "Windows":
                cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
            else:
                cap = cv2.VideoCapture(i)
                
            if cap.isOpened():
                ret, frame = cap.read()
                if ret:
                    available_cameras.append(i)
                cap.release()
        
        print(f"Available cameras: {available_cameras}")
        return available_cameras
        
    except Exception as e:
        print(f"Error checking camera permissions: {e}")
        return []

# Diagnostic function
def diagnose_camera_issues():
    """Comprehensive camera diagnostics"""
    print("=== CAMERA DIAGNOSTICS ===")
    
    # System information
    print(f"System: {platform.system()} {platform.release()}")
    print(f"Python version: {sys.version.split()[0]}")
    print(f"OpenCV version: {cv2.__version__}")
    
    # Check available cameras
    available_cameras = check_camera_permissions()
    print(f"Detected cameras: {available_cameras}")
    
    # Camera permission guidance
    if platform.system() == "Windows":
        print("\nWindows Camera Permissions:")
        print("1. Go to Settings → Privacy & Security → Camera")
        print("2. Ensure 'Camera access' is ON")
        print("3. Ensure 'Let apps access your camera' is ON")
        print("4. Make sure Python/your IDE has camera access")
    elif platform.system() == "Darwin":  # macOS
        print("\nmacOS Camera Permissions:")
        print("1. Go to System Preferences → Security & Privacy → Privacy")
        print("2. Select Camera from the left sidebar")
        print("3. Check the box next to your Python IDE or Terminal")
    else:  # Linux
        print("\nLinux Camera Access:")
        print("1. Check permissions with: v4l2-ctl --list-devices")
        print("2. Ensure user is in the 'video' group: sudo usermod -aG video $USER")
    
    # Try to open default camera
    print("\nTesting camera index 0:")
    try:
        if platform.system() == "Windows":
            cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        else:
            cap = cv2.VideoCapture(0)
            
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                print("✓ Camera opens and reads frames successfully!")
                print(f"  Frame dimensions: {frame.shape[1]}x{frame.shape[0]}")
            else:
                print("✗ Camera opens but cannot read frames")
            cap.release()
        else:
            print("✗ Cannot open camera index 0")
    except Exception as e:
        print(f"✗ Error testing camera: {e}")
    
    print("=== END DIAGNOSTICS ===")

def get_diagnostic_report():
    """Capture diagnostic output as a string"""
    f = io.StringIO()
    with redirect_stdout(f):
        # Suppress OpenCV errors during diagnostics
        original_stderr = sys.stderr
        sys.stderr = io.StringIO()
        try:
            diagnose_camera_issues()
        finally:
            # Restore stderr
            sys.stderr = original_stderr
    return f.getvalue()

# Gradio Interface
with gr.Blocks(title="Webcam Application", css="footer {visibility: hidden}") as demo:
    gr.Markdown("## 📷 Webcam Control Panel")
    
    with gr.Row():
        webcam_feed = gr.Image(
            label="Camera Feed", 
            value=last_frame,
            height=480,
            width=640
        )
        
    with gr.Row():
        start_btn = gr.Button("🚀 Start Webcam", variant="primary")
        stop_btn = gr.Button("⏹️ Stop Webcam", variant="secondary")
        diag_btn = gr.Button("🔍 Run Diagnostics", variant="secondary")
    
    diag_output = gr.Textbox(label="Diagnostics Report", lines=12, interactive=False)
    
    # Real-time updates
    demo.load(
        fn=lambda: get_webcam_frame(),
        inputs=None,
        outputs=webcam_feed,
        every=100  # Update every 100ms (10fps)
    )
    
    # Button actions
    start_btn.click(
        fn=start_webcam,
        inputs=None,
        outputs=webcam_feed
    )
    
    stop_btn.click(
        fn=stop_webcam,
        inputs=None,
        outputs=webcam_feed
    )
    
    diag_btn.click(
        fn=get_diagnostic_report,
        inputs=None,
        outputs=diag_output
    )

if __name__ == "__main__":
    # Instead of running diagnostics directly, launch the Gradio app
    demo.launch()