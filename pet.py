import tkinter as tk
import threading
import time
import psutil  # pip install psutil
import sys
import socket
import platform
import tkinter.font as tkFont

# For Windows: import to get active window info
if platform.system() == "Windows":
    import ctypes
    import ctypes.wintypes

    user32 = ctypes.windll.user32
    kernel32 = ctypes.windll.kernel32

    GetForegroundWindow = user32.GetForegroundWindow
    GetWindowTextLengthW = user32.GetWindowTextLengthW
    GetWindowTextW = user32.GetWindowTextW

    def get_active_window_title():
        hwnd = GetForegroundWindow()
        length = GetWindowTextLengthW(hwnd)
        buff = ctypes.create_unicode_buffer(length + 1)
        GetWindowTextW(hwnd, buff, length + 1)
        return buff.value

else:
    # Fallback for other OSes (Linux/Mac) - returns None, no tracking
    def get_active_window_title():
        return None

# === Your faces dict ===
faces_dict = {
    1: {"face": "(⇀‿‿↼)", "mood": "sleeping - late night, low activity"},
    2: {"face": "(≖‿‿≖)", "mood": "awakening - just woke up"},
    3: {"face": "(◕‿‿◕)", "mood": "awake / normal - casual use"},
    4: {"face": "(⚆⚆)", "mood": "observing (neutral mood) - app switched"},
    5: {"face": "(☉☉)", "mood": "observing (neutral mood) - idle for a bit"},
    6: {"face": "(◕‿◕)", "mood": "observing (happy) - using productive app"},
    7: {"face": "(◕‿―)", "mood": "observing (happy) - long session on productive app"},
    8: {"face": "(°▃▃°)", "mood": "intense - high CPU or stressed"},
    9: {"face": "(⌐■_■)", "mood": "cool - focused, deep work"},
    10: {"face": "(•‿‿•)", "mood": "happy - relaxed and chill"},
    11: {"face": "(^‿‿^)", "mood": "grateful - nice break"},
    12: {"face": "(ᵔ◡◡ᵔ)", "mood": "excited - just started a new app"},
    13: {"face": "(✜‿‿✜)", "mood": "smart - coding or math app active"},
    14: {"face": "(♥‿‿♥)", "mood": "friendly - chatting/social app active"},
    15: {"face": "(☼‿‿☼)", "mood": "motivated - morning energy"},
    16: {"face": "(≖__≖)", "mood": "demotivated - tired, late day"},
    17: {"face": "(-__-)", "mood": "bored - idle for a long time"},
    18: {"face": "(╥☁╥)", "mood": "sad - long break, no activity"},
    19: {"face": "(ب__ب)", "mood": "lonely - no apps used for long"},
    20: {"face": "(☓‿‿☓)", "mood": "broken - error state or crash"},
    21: {"face": "(#__#)", "mood": "debugging - coding session"},
}

# === Globals ===
current_face_num = 1
custom_face = None
scale = 1.0

# Track active app and duration
active_app = None
app_start_time = None

# Productive and social app keywords
productive_apps_keywords = ["code", "pycharm", "visual studio", "mathematica", "terminal", "bash", "python", "jupyter", "vscode", "sublime"]
social_apps_keywords = ["discord", "slack", "telegram", "whatsapp", "zoom", "skype", "teams"]
chatting_apps_keywords = social_apps_keywords

# === Tkinter main window setup ===
root = tk.Tk()
root.overrideredirect(True)
root.attributes('-topmost', True)
root.resizable(False, False)
TRANSPARENT_COLOR = 'magenta'
root.config(bg=TRANSPARENT_COLOR)
root.attributes('-transparentcolor', TRANSPARENT_COLOR)

corner_radius = 30
padding = 3

canvas_width = int(150 * scale)
canvas_height = int(75 * scale)

canvas = tk.Canvas(root, width=canvas_width, height=canvas_height, bg=TRANSPARENT_COLOR, highlightthickness=0)
canvas.pack()

def draw_rounded_rect(x1, y1, x2, y2, r, **kwargs):
    points = [
        x1+r, y1,
        x1+r, y1,
        x2-r, y1,
        x2-r, y1,
        x2, y1,
        x2, y1+r,
        x2, y1+r,
        x2, y2-r,
        x2, y2-r,
        x2, y2,
        x2-r, y2,
        x2-r, y2,
        x1+r, y2,
        x1+r, y2,
        x1, y2,
        x1, y2-r,
        x1, y2-r,
        x1, y1+r,
        x1, y1+r,
        x1, y1
    ]
    return canvas.create_polygon(points, smooth=True, **kwargs)

face_label = tk.Label(canvas, text=faces_dict[current_face_num]["face"], font=("Courier", int(28*scale), "bold"), bg="white", fg="black")
face_label.place(relx=0.5, rely=0.5, anchor="center")

def get_widest_face_width(current_scale):
    font = tkFont.Font(family="Courier", size=int(28 * current_scale), weight="bold")
    max_width = 0
    for face_info in faces_dict.values():
        face_text = face_info["face"]
        width = font.measure(face_text)
        if width > max_width:
            max_width = width
    if custom_face:
        custom_width = font.measure(custom_face)
        if custom_width > max_width:
            max_width = custom_width
    return max_width

def update_canvas_size(current_scale):
    global canvas_width, canvas_height
    base_width = int(150 * current_scale)
    base_height = int(75 * current_scale)
    widest_face_px = get_widest_face_width(current_scale) + 40  # add some padding

    canvas_width = max(base_width, widest_face_px)
    canvas_height = base_height

    canvas.config(width=canvas_width, height=canvas_height)
    canvas.delete("all")
    draw_rounded_rect(padding, padding, canvas_width - padding, canvas_height - padding, corner_radius, fill="white", outline="black")

    face_label.config(font=("Courier", int(28 * current_scale), "bold"), bg="white")
    face_label.place(relx=0.5, rely=0.5, anchor="center")

# Move window logic
def start_move(event):
    root.x_start = event.x
    root.y_start = event.y

def do_move(event):
    x = root.winfo_x() + (event.x - root.x_start)
    y = root.winfo_y() + (event.y - root.y_start)
    root.geometry(f"+{x}+{y}")

canvas.bind("<ButtonPress-1>", start_move)
canvas.bind("<B1-Motion>", do_move)
face_label.bind("<ButtonPress-1>", start_move)
face_label.bind("<B1-Motion>", do_move)

# Face setters
def set_face_by_number(num):
    global current_face_num, custom_face
    if num in faces_dict:
        current_face_num = num
        custom_face = None
        face_label.config(text=faces_dict[num]["face"])
        update_canvas_size(scale)
        log(f"Set face to #{num}: {faces_dict[num]['face']}")
    else:
        log(f"Face number {num} does not exist.")

def set_custom_face(face_str):
    global custom_face
    custom_face = face_str
    face_label.config(text=face_str)
    update_canvas_size(scale)
    log(f"Set custom face: {face_str}")

def log(msg):
    print(msg)

# === Mood logic ===
def time_based_face():
    hour = time.localtime().tm_hour
    if 6 <= hour < 12:
        set_face_by_number(15)  # motivated morning
    elif 12 <= hour < 18:
        set_face_by_number(10)  # happy afternoon
    elif 18 <= hour < 22:
        set_face_by_number(8)   # intense evening
    else:
        set_face_by_number(1)   # sleepy night

def system_mood():
    cpu_load = psutil.cpu_percent(interval=1)
    if cpu_load > 75:
        set_face_by_number(8)  # intense face if CPU is busy
    elif cpu_load < 10:
        set_face_by_number(3)  # normal/chill face if CPU is free

def app_tracking_mood():
    global active_app, app_start_time

    current_app = get_active_window_title()
    now = time.time()

    if current_app is None or current_app.strip() == "":
        set_face_by_number(19)  # lonely - no app info
        active_app = None
        app_start_time = None
        return

    current_app_lower = current_app.lower()

    if active_app != current_app_lower:
        active_app = current_app_lower
        app_start_time = now
        log(f"App switched to: {current_app}")

        if any(keyword in current_app_lower for keyword in productive_apps_keywords):
            set_face_by_number(12)  # excited - new productive app
        elif any(keyword in current_app_lower for keyword in chatting_apps_keywords):
            set_face_by_number(14)  # friendly - chatting app active
        else:
            set_face_by_number(4)  # observing neutral - other app
    else:
        duration = now - app_start_time
        if any(keyword in current_app_lower for keyword in productive_apps_keywords):
            if duration < 60*10:
                set_face_by_number(6)
            else:
                set_face_by_number(7)
        elif any(keyword in current_app_lower for keyword in chatting_apps_keywords):
            if duration < 60*5:
                set_face_by_number(14)
            else:
                set_face_by_number(11)
        else:
            if duration < 60*3:
                set_face_by_number(4)
            elif duration < 60*15:
                set_face_by_number(5)
            else:
                set_face_by_number(17)

def pet_mood_loop():
    while True:
        app_tracking_mood()
        system_mood()
        time.sleep(15)

threading.Thread(target=pet_mood_loop, daemon=True).start()

# === Settings window ===
settings_window = None

def open_settings_window():
    global settings_window
    if settings_window and settings_window.winfo_exists():
        settings_window.lift()
        return
    settings_window = tk.Toplevel(root)
    settings_window.title("Settings")
    settings_window.geometry("300x220")
    settings_window.resizable(False, False)

    tk.Label(settings_window, text="Scale (0.5 to 3.0):").pack(pady=10)

    scale_var = tk.DoubleVar(value=scale)
    scale_slider = tk.Scale(settings_window, from_=0.5, to=3.0, resolution=0.1, orient=tk.HORIZONTAL, variable=scale_var)
    scale_slider.pack(padx=20)

    def apply_settings():
        global scale
        scale = scale_var.get()
        update_canvas_size(scale)
        settings_window.destroy()

    def reset_scale():
        scale_var.set(1.0)
        apply_settings()  # apply reset immediately

    apply_btn = tk.Button(settings_window, text="Apply", command=apply_settings)
    apply_btn.pack(pady=(10, 5))

    reset_btn = tk.Button(settings_window, text="Reset Scale", command=reset_scale, fg="crimson")
    reset_btn.pack(pady=(0, 10))

# Bind shortcut Ctrl+S to open settings window
root.bind("<Control-s>", lambda e: open_settings_window())

# Initialize canvas size and background shape
update_canvas_size(scale)

# Show initial face
set_face_by_number(current_face_num)

# Start the Tkinter event loop
root.mainloop()
