import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import socket
import threading
import psutil
import time

HOST = '127.0.0.1'
PORT = 65432

class DevMenu(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Pet DevMenu")
        self.geometry("470x520")
        self.resizable(False, True)

        self.current_face_num = None
        self.current_face_str = ""
        self.face_reason = "Face info will appear here."
        self.face_source = "auto"  # could be "cpu", "app_time", "manual", or "default"
        self.is_cycle_reset = False  # Track if reset was pressed

        # Current face display at top
        tk.Label(self, text="Current Face:", font=("Arial", 12, "bold")).pack(pady=(10,0))
        self.current_face_label = tk.Label(self, text="", font=("Courier", 36))
        self.current_face_label.pack()

        # Why this face? explanation under current face
        tk.Label(self, text="Why this face?", font=("Arial", 10, "italic"), fg="purple").pack()
        self.face_reason_label = tk.Label(self, text=self.face_reason, wraplength=440, justify="center", fg="purple")
        self.face_reason_label.pack(pady=(0,10))

        # Face dropdown
        tk.Label(self, text="Select Face:").pack(pady=(0,0))
        self.face_dropdown = ttk.Combobox(self, state="readonly")
        self.face_dropdown.pack()
        self.face_dropdown.bind("<<ComboboxSelected>>", self.on_face_select)

        # Current time display
        tk.Label(self, text="Current Time:").pack(pady=(10,0))
        self.time_label = tk.Label(self, text="", font=("Courier", 12, "bold"), fg="darkgreen")
        self.time_label.pack()

        # Custom face entry
        tk.Label(self, text="Or enter custom face:").pack(pady=(10,0))
        self.custom_entry = tk.Entry(self)
        self.custom_entry.pack()

        # Buttons for face control
        self.set_face_btn = tk.Button(self, text="Set Face", command=self.set_face)
        self.set_face_btn.pack(pady=5)
        self.set_custom_btn = tk.Button(self, text="Set Custom Face", command=self.set_custom_face)
        self.set_custom_btn.pack(pady=5)

        # Scale control slider
        tk.Label(self, text="Set Scale (if supported):").pack(pady=(10,0))
        self.scale_var = tk.DoubleVar(value=1.0)
        self.scale_slider = tk.Scale(self, from_=0.5, to=3.0, resolution=0.1, orient=tk.HORIZONTAL, variable=self.scale_var)
        self.scale_slider.pack()
        self.scale_btn = tk.Button(self, text="Apply Scale", command=self.set_scale)
        self.scale_btn.pack(pady=5)

        # Device info display
        tk.Label(self, text="Device Info:").pack(pady=(10,0))
        self.device_info = tk.Label(self, text="", justify="left", font=("Courier", 10))
        self.device_info.pack()

        self.refresh_info_btn = tk.Button(self, text="Refresh Device Info", command=self.update_device_info)
        self.refresh_info_btn.pack(pady=5)

        # Quit & Restart buttons
        self.quit_btn = tk.Button(self, text="Quit Pet App", fg="red", command=self.quit_pet)
        self.quit_btn.pack(pady=(10,0))
        self.restart_btn = tk.Button(self, text="Restart Face Cycle", command=self.restart_cycle)
        self.restart_btn.pack()

        # Logs
        self.log_box = scrolledtext.ScrolledText(self, height=8, state='disabled')
        self.log_box.pack(pady=(10,0), fill='both', expand=True)

        # Connect to pet.py server
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.connect((HOST, PORT))
        except ConnectionRefusedError:
            messagebox.showerror("Error", "Could not connect to pet.py server.\nMake sure pet.py is running.")
            self.destroy()
            return

        threading.Thread(target=self.receive_messages, daemon=True).start()
        self.request_faces()

        # Start periodic updates
        self.after(1000, self.update_time)
        self.after(5000, self.update_device_info_periodic)
        self.after(3000, self.check_cpu_and_update_face)  # check CPU usage every 3 sec to update face reason

    def request_faces(self):
        try:
            self.sock.sendall(b"get_faces")
        except:
            self.log("Failed to request faces from pet.py")

    def receive_messages(self):
        while True:
            try:
                data = self.sock.recv(4096)
                if not data:
                    break
                message = data.decode('utf-8')
                self.log(f"Pet.py: {message}")

                if message.startswith("1:"):
                    self.faces = {}
                    pairs = message.split(",")
                    face_list = []
                    for p in pairs:
                        num, face = p.split(":", 1)
                        self.faces[int(num)] = face
                        face_list.append(f"{num}: {face}")
                    self.face_dropdown['values'] = face_list
                    if face_list:
                        self.face_dropdown.current(0)
                        first_num = int(face_list[0].split(":")[0])
                        self.update_current_face(first_num, self.faces[first_num], "auto")
                        self.is_cycle_reset = False  # reset flag because face updated normally

            except:
                break

    def on_face_select(self, event):
        sel = self.face_dropdown.get()
        if sel:
            num = int(sel.split(":")[0])
            face_str = self.faces.get(num, "")
            self.update_current_face(num, face_str, "manual")
            self.is_cycle_reset = False  # manual selection clears reset state

    def update_current_face(self, face_num, face_str, source):
        self.current_face_num = face_num
        self.current_face_str = face_str
        self.face_source = source

        self.current_face_label.config(text=face_str)

        # If cycle was reset, show default face message until face changes
        if self.is_cycle_reset:
            self.face_reason_label.config(text="Default face")
        else:
            reason = self.get_face_reason(face_num, source)
            self.face_reason_label.config(text=reason)

    def get_face_reason(self, face_num, source):
        # You can expand this with real CPU or app logic.
        if self.is_cycle_reset:
            # If reset cycle pressed, always show default
            return "Default face"
        if source == "manual":
            return "Face set manually via DevMenu."
        elif source == "cpu":
            return "High CPU load detected, face reflects stress."
        elif source == "app_time":
            return "You've been using Discord for 2 hours — pet senses it!"
        else:  # auto or default
            reasons = {
                1: "Sleepy and resting — night time mood.",
                2: "Just woke up — morning vibes.",
                3: "Chill and awake.",
                4: "Observing neutrally.",
                5: "Curious gaze.",
                6: "Happy and friendly.",
                7: "Playful wink.",
                8: "Focused and intense (CPU busy).",
                9: "Cool with shades on.",
                10: "Happy afternoon mood.",
                11: "Feeling thankful.",
                12: "Excited and energetic!",
                13: "Smart and clever.",
                14: "Friendly and loving.",
                15: "Motivated morning energy.",
                16: "A bit demotivated — maybe rest?",
                17: "Bored and uninterested.",
                18: "Sad — hugs needed.",
                19: "Lonely but hopeful.",
                20: "Tired and broken.",
                21: "Debugging mode active."
            }
            return reasons.get(face_num, "This face shows a unique mood!")

    def update_time(self):
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.config(text=now)
        self.after(1000, self.update_time)

    def set_face(self):
        sel = self.face_dropdown.get()
        if not sel:
            self.log("No face selected.")
            return
        num = int(sel.split(":")[0])
        cmd = f"set_face {num}"
        self.send_command(cmd)
        self.log(f"Sent command: {cmd}")
        self.update_current_face(num, self.faces[num], "manual")
        self.is_cycle_reset = False

    def set_custom_face(self):
        face = self.custom_entry.get().strip()
        if not face:
            self.log("Custom face is empty.")
            return
        cmd = f"set_custom_face {face}"
        self.send_command(cmd)
        self.log(f"Sent command: {cmd}")
        self.current_face_label.config(text=face)
        self.face_reason_label.config(text="Custom face set manually via DevMenu.")
        self.face_source = "manual"
        self.is_cycle_reset = False

    def set_scale(self):
        scale = self.scale_var.get()
        cmd = f"set_scale {scale}"
        self.send_command(cmd)
        self.log(f"Sent command: {cmd}")

    def update_device_info(self):
        cpu = psutil.cpu_percent(interval=0.5)
        mem = psutil.virtual_memory()
        info_text = (
            f"CPU Usage: {cpu}%\n"
            f"Memory Usage: {mem.percent}%\n"
            f"IP Address: {self.get_ip_address()}\n"
        )
        self.device_info.config(text=info_text)

    def update_device_info_periodic(self):
        self.update_device_info()
        self.after(5000, self.update_device_info_periodic)

    def get_ip_address(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.settimeout(0)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "Unavailable"

    def quit_pet(self):
        self.send_command("quit")
        self.log("Sent quit command.")

    def restart_cycle(self):
        # When user presses reset, send command and set flag to show "Default face"
        self.send_command("restart_cycle")
        self.log("Sent restart cycle command.")
        self.is_cycle_reset = True
        self.current_face_label.config(text="")  # Clear current face display until update
        self.face_reason_label.config(text="Default face")

    def send_command(self, cmd):
        try:
            self.sock.sendall(cmd.encode('utf-8'))
        except Exception as e:
            self.log(f"Failed to send command: {e}")

    def log(self, msg):
        self.log_box.config(state='normal')
        self.log_box.insert(tk.END, msg + "\n")
        self.log_box.see(tk.END)
        self.log_box.config(state='disabled')

    def check_cpu_and_update_face(self):
        # Optional: check CPU usage, update face reason accordingly if in auto mode
        cpu = psutil.cpu_percent(interval=0)
        if cpu > 75:
            # High CPU usage face update if face is auto or cpu-based
            if self.face_source != "manual" and not self.is_cycle_reset:
                # Let's say face_num 8 is "Focused and intense (CPU busy)"
                self.update_current_face(8, self.faces.get(8, "😠"), "cpu")
        else:
            # Only revert to auto face if not manual or reset
            if self.face_source == "cpu" and not self.is_cycle_reset:
                # Revert to first face in list (or keep current)
                if self.faces:
                    first_num = sorted(self.faces.keys())[0]
                    self.update_current_face(first_num, self.faces[first_num], "auto")
        self.after(3000, self.check_cpu_and_update_face)

if __name__ == "__main__":
    app = DevMenu()
    app.mainloop()
