import threading
import subprocess
import os
import time
import random
import psutil
import speech_recognition as sr
import pyttsx3
import customtkinter as ctk
from google import genai
from google.genai import types
from dotenv import load_dotenv
from PIL import Image, ImageTk

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# --- AI TOOL DEFINITION ---
def execute_system_command(app_name: str) -> str:
    """Autonomous tool for system control and hardware health."""
    app_name = app_name.lower()
    
    # Feature: System Health Check
    if any(word in app_name for word in ["status", "health", "battery", "cpu"]):
        cpu = psutil.cpu_percent(interval=1)
        bat = psutil.sensors_battery()
        percent = bat.percent if bat else "N/A"
        plugged = "Plugged In" if bat and bat.power_plugged else "On Battery"
        return f"System Report: CPU usage is at {cpu}%. Battery is at {percent}% ({plugged})."

    # Feature: App Launcher
    try:
        os.startfile(app_name)
        return f"SUCCESS: System has initialized {app_name}."
    except Exception:
        try:
            subprocess.Popen([f"{app_name}.exe"])
            return f"SUCCESS: Initialized {app_name} via fallback."
        except:
            return f"ERROR: System could not locate {app_name}."

# --- LOGIN INTERFACE ---
class LoginPage(ctk.CTk):
    def __init__(self, on_success):
        super().__init__()
        self.on_success = on_success
        self.title("NEURAL-CORE: AUTHENTICATION")
        self.geometry("450x700")
        self.configure(fg_color="#0A0A0B")
        
        self.canvas = ctk.CTkCanvas(self, bg="#0A0A0B", highlightthickness=0)
        self.canvas.place(relx=0, rely=0, relwidth=1, relheight=1)

        try:
            raw_img = Image.open("1000055019.jpg")
            self.char_img = ctk.CTkImage(light_image=raw_img, dark_image=raw_img, size=(280, 400))
            ctk.CTkLabel(self, image=self.char_img, text="").pack(pady=(30, 10))
        except:
            print("Login image (1000055019.jpg) missing.")

        ctk.CTkLabel(self, text="USER LOGIN", font=("Consolas", 20, "bold"), text_color="#00FBFF").pack(pady=10)
        
        self.user = ctk.CTkEntry(self, placeholder_text="Username", width=280, height=40, border_color="#005F73")
        self.user.pack(pady=10)
        
        self.pwd = ctk.CTkEntry(self, placeholder_text="Password", show="*", width=280, height=40, border_color="#005F73")
        self.pwd.pack(pady=10)

        ctk.CTkButton(self, text="ACCESS SYSTEM", fg_color="#005F73", hover_color="#00FBFF", 
                      width=200, height=45, command=self.check_auth).pack(pady=30)

    def check_auth(self):
        if self.user.get() == "admin" and self.pwd.get() == "1234":
            self.destroy()
            self.on_success()
        else:
            self.user.configure(border_color="red")
            self.pwd.configure(border_color="red")

# --- MAIN ASSISTANT ---
class RoboticAIAssistant(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("NEURAL-CORE: AI ASSISTANT")
        self.geometry("950x850")
        self.resizable(True, True)
        ctk.set_appearance_mode("dark")

        self.CYAN, self.DARK_CYAN, self.BG_COLOR = "#00FBFF", "#005F73", "#0A0A0B"
        self.is_listening = False
        self.pulse_val = 0
        
        self.canvas = ctk.CTkCanvas(self, bg=self.BG_COLOR, highlightthickness=0)
        self.canvas.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.output_log = ctk.CTkTextbox(self, width=850, height=250, fg_color="#121214", 
                                          border_width=2, border_color=self.DARK_CYAN, 
                                          font=("Consolas", 14), text_color=self.CYAN)
        self.output_log.pack(padx=20, pady=(350, 20))
        
        self.input_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.input_frame.pack(pady=(0, 20), side="bottom")

        self.input_field = ctk.CTkEntry(self.input_frame, width=550, height=45, border_color=self.DARK_CYAN)
        self.input_field.pack(side="left", padx=10)
        self.input_field.bind("<Return>", lambda e: self.process_text_input())
        
        self.listen_btn = ctk.CTkButton(self.input_frame, text="TAP TO SPEAK", command=self.start_listening_thread)
        self.listen_btn.pack(side="left", padx=10)

        self.engine = pyttsx3.init()
        self.recognizer = sr.Recognizer()
        self.client = genai.Client(api_key=GEMINI_API_KEY)
        self.chat_session = self.client.chats.create(
            model="gemini-3-flash-preview", 
            config=types.GenerateContentConfig(tools=[execute_system_command])
        )

        self.log_message("SYSTEM INITIALIZED. NEURAL LINK SECURE.")
        self.update_ui_animation()

    def log_message(self, msg):
        self.output_log.insert("end", f"[{time.strftime('%H:%M:%S')}] > {msg}\n")
        self.output_log.see("end")

    def speak(self, text):
        self.log_message(f"AI: {text}")
        self.engine.say(text)
        self.engine.runAndWait()

    def update_ui_animation(self):
        self.canvas.delete("core")
        cx = self.canvas.winfo_width() // 2 if self.winfo_width() > 1 else 475
        cy = 180 

        # Tech Grid
        for i in range(0, 2000, 100):
            self.canvas.create_line(i, 0, i, 2000, fill="#161618", width=1, tags="core")
            self.canvas.create_line(0, i, 2000, i, fill="#161618", width=1, tags="core")

        # Rotating Arcs
        angle = (time.time() * 100) % 360
        self.canvas.create_arc(cx-110, cy-110, cx+110, cy+110, start=angle, extent=90, outline=self.CYAN, width=2, style="arc", tags="core")
        self.canvas.create_arc(cx-110, cy-110, cx+110, cy+110, start=angle+180, extent=90, outline=self.CYAN, width=2, style="arc", tags="core")

        if self.is_listening:
            self.pulse_val = (self.pulse_val + 5) % 100
            aura = 110 + (self.pulse_val // 2)
            self.canvas.create_oval(cx-aura, cy-aura, cx+aura, cy+aura, outline=self.DARK_CYAN, tags="core")
            self.canvas.create_text(cx, 60, text="LISTENING FOR SIGNAL...", fill="white", font=("Consolas", 18), tags="core")

        self.canvas.create_oval(cx-100, cy-100, cx+100, cy+100, outline=self.CYAN, width=3, tags="core")
        self.canvas.create_oval(cx-35, cy-35, cx+35, cy+35, fill=self.CYAN if self.is_listening else self.DARK_CYAN, tags="core")

        self.after(50, self.update_ui_animation)

    def start_listening_thread(self):
        self.is_listening = True
        threading.Thread(target=self.listen_voice, daemon=True).start()

    def listen_voice(self):
        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source)
            try:
                audio = self.recognizer.listen(source, timeout=5)
                query = self.recognizer.recognize_google(audio)
                self.is_listening = False
                self.master_logic(query)
            except:
                self.is_listening = False

    def master_logic(self, query):
        try:
            response = self.chat_session.send_message(query)
            self.speak(response.text)
        except Exception as e:
            self.log_message(f"NEURAL_ERROR: {e}")

    def process_text_input(self):
        query = self.input_field.get()
        if query:
            self.log_message(f"USER_INPUT: {query}")
            self.input_field.delete(0, 'end')
            threading.Thread(target=self.master_logic, args=(query,), daemon=True).start()

if __name__ == "__main__":
    login = LoginPage(on_success=lambda: RoboticAIAssistant().mainloop())
    login.mainloop()