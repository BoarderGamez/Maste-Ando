import tkinter as tk
import random

# --- Faces dictionary ---
faces_dict = {
    1: {"face": "(⇀‿‿↼)", "mood": "sleeping"},
    2: {"face": "(≖‿‿≖)", "mood": "awakening"},
    3: {"face": "(◕‿‿◕)", "mood": "awake / normal"},
    4: {"face": "(⚆⚆)", "mood": "observing (neutral mood)"},
    5: {"face": "(☉☉)", "mood": "observing (neutral mood)"},
    6: {"face": "(◕‿◕)", "mood": "observing (happy)"},
    7: {"face": "(◕‿―)", "mood": "observing (happy)"},
    8: {"face": "(°▃▃°)", "mood": "intense"},
    9: {"face": "(⌐■_■)", "mood": "cool"},
    10: {"face": "(•‿‿•)", "mood": "happy"},
    11: {"face": "(^‿‿^)", "mood": "grateful"},
    12: {"face": "(ᵔ◡◡ᵔ)", "mood": "excited"},
    13: {"face": "(✜‿‿✜)", "mood": "smart"},
    14: {"face": "(♥‿‿♥)", "mood": "friendly"},
    15: {"face": "(☼‿‿☼)", "mood": "motivated"},
    16: {"face": "(≖__≖)", "mood": "demotivated"},
    17: {"face": "(-__-)", "mood": "bored"},
    18: {"face": "(╥☁╥)", "mood": "sad"},
    19: {"face": "(ب__ب)", "mood": "lonely"},
    20: {"face": "(☓‿‿☓)", "mood": "broken"},
    21: {"face": "(#__#)", "mood": "debugging"}
}

# --- Setup window ---
root = tk.Tk()
root.overrideredirect(True)
root.attributes('-topmost', True)
root.resizable(False, False)

TRANSPARENT_COLOR = 'magenta'
root.config(bg=TRANSPARENT_COLOR)
root.attributes('-transparentcolor', TRANSPARENT_COLOR)

canvas_width = 150
canvas_height= 75
corner_radius = 30
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

draw_rounded_rect(0, 0, canvas_width, canvas_height, corner_radius, fill="white", outline="black")

# --- Pet face label ---
# Start with face #1 as default
current_face_num = 1

face_label = tk.Label(
    canvas,
    text=faces_dict[current_face_num]["face"],
    font=("Courier", 28, "bold"),
    bg="white",
    fg="black"
)
face_label.place(relx=0.5, rely=0.5, anchor="center")

# --- Dragging logic ---
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

# --- New function: Set face by number ---
def set_face_by_number(num):
    global current_face_num
    if num in faces_dict:
        current_face_num = num
        face_label.config(text=faces_dict[num]["face"])
    else:
        print(f"Face number {num} does not exist.")

# Remove double-click random face change (commented out)
# def change_mood(event=None):
#     face_label.config(text=random.choice(faces))

# canvas.bind("<Double-Button-1>", change_mood)
# face_label.bind("<Double-Button-1>", change_mood)

# --- Run ---
root.mainloop()
