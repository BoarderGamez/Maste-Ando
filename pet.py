import tkinter as tk
import random

# --- Faces list (Pwnagotchi inspired) ---
faces = [
    "(⇀‿‿↼)",  # sleeping
    "(≖‿‿≖)",  # awakening
    "(◕‿‿◕)",  # awake
    "(°▃▃°)",  # intense
    "(⌐■_■)",  # cool
    "(•‿‿•)",  # happy
    "(╥☁╥)",  # sad
    "(☼‿‿☼)",  # motivated
    "(-__-)",  # bored
]

# --- Setup window ---
root = tk.Tk()
root.overrideredirect(True)   # Remove window borders
root.attributes('-topmost', True)  # Always on top
root.resizable(False, False)  # Not resizable
root.configure(bg="white")

TRANSPARENT_COLOR = 'magenta'
root.config(bg=TRANSPARENT_COLOR)
root.attributes('-transparentcolor', TRANSPARENT_COLOR)
# --- Create canvas with rounded corners ---
canvas_width = 150
canvas_height= 75
corner_radius = 30
canvas = tk.Canvas(root, width=canvas_width, height=canvas_height, bg=TRANSPARENT_COLOR, highlightthickness=0)
canvas.pack()

# Draw rounded background
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
face_label = tk.Label(
    canvas,
    text=random.choice(faces),
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

# --- Change mood on double-click ---
def change_mood(event=None):
    face_label.config(text=random.choice(faces))

canvas.bind("<Double-Button-1>", change_mood)
face_label.bind("<Double-Button-1>", change_mood)

# --- Run ---
root.mainloop()
