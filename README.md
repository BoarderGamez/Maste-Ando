# Maste Ando
A cute floating pwnagotchi like desktop pet that changes mood based on your system activity, active apps, and CPU load — with sassy vibes and smart behavior. Made with Tkinter + psutil + a sprinkle of magic!

# Features
* Shows different faces to represent your mood throughout the day
* Detects active application windows (Windows only) to switch moods accordingly
* Reflects system CPU load with intense or chill faces
* Tracks time spent on apps and updates moods
* Transparent, draggable window with rounded corners
* Keyboard shortcut Ctrl + Shift + S to open scale settings for resizing
* Right-click anywhere on the face or background to close the app
* Socket server for remote face control and scale adjustment

# How to Run
Make sure you have Python installed (recommended 3.7+)
## How to Run


##  Install dependencies:  
   ```pip install psutil```
## Settings Window

- Opens with **Ctrl + Shift + S**  
- Adjust the scale (0.5 to 3.0) to resize the widget dynamically  
- Click **Apply** to save changes  
- Click **Reset Scale** to go back to default size (1.0)  

---

## Remote Commands (Socket Server)

Server listens on `127.0.0.1:65432` for these commands:

| Command                 | Description                     |
|-------------------------|--------------------------------|
| `get_faces`             | Returns all face IDs and their emojis |
| `set_face <num>`        | Sets face by number             |
| `set_custom_face <face>`| Sets a custom face string       |
| `set_scale <value>`     | Adjust the scale dynamically    |

---

## Notes

- Active window detection works best on **Windows**; other OSes fallback with limited functionality.  
- The window is transparent with rounded corners for style.  
- The faces and moods can be customized inside the `faces_dict` in the code.

---

## Customize & Extend

Feel free to add more moods, faces, or app keywords in the code to match your vibe!  
Want to change how the mood logic works? Just tweak the functions: `time_based_face()`, `system_mood()`, `app_tracking_mood()`.

---

## License

Free to use, share, and remix!  
Made with love by me

---

If you want me to help with updates or features, just shout!
