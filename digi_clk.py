#digital clock with alarm support

import tkinter as tk  
from tkinter import messagebox, ttk  
import datetime
import threading
import time
import pygame
import os

class DigitalClock:
    def __init__(self, root):
        # save the Tk root and give the window a friendly title
        self.root = root
        self.root.title("digi-alarm clock")

        # Start windowed. The user can press F11 to go full screen and Escape to return.
        self.root.geometry("1280x720")
        # Keep the real screen size available if we need it later
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()

        # Allow resizing so the maximize button is enabled
        self.root.resizable(True, True)
        self.root.configure(bg='black')

        # Big green digital-style time label for the clock (created early so update_clock can use it)
        self.time_label = tk.Label(self.root, font=('Ubuntu', 120, 'bold'),
                                   fg='#00FF00', bg='black')
        self.time_label.pack(pady=50)

        # Initialize pygame mixer for alarm sound playback (if available)
        pygame.mixer.init()

        # Use 24-hour format by default; users can toggle to 12-hour
        self.time_format_24 = True

        # Container for alarms. Each alarm is a dict with keys: time_24h, display, active
        self.alarms = []

        # Track fullscreen state explicitly and remember previous geometry so
        # we can restore the window after leaving fullscreen.
        self.is_fullscreen = False
        self.previous_geometry = self.root.geometry()

        # A small control area for toggling time format
        format_frame = tk.Frame(root, bg='black')
        format_frame.pack(pady=20)

        self.format_btn = tk.Button(
            format_frame, text="switch to 12H",
            command=self.toggle_time_format,
            font=('Ubuntu', 16),
            bg='#003300', fg='#00FF00',
            activebackground='#006600', activeforeground='#00FF00',
            padx=20, pady=10
        )
        self.format_btn.pack()

        # Alarm entry area (hours:minutes:seconds)
        alarm_frame = tk.Frame(root, bg='black')
        alarm_frame.pack(pady=30)

        tk.Label(alarm_frame, text="alarm timer (H:M:S)",
                 font=('Ubuntu', 20), fg='white', bg='black').grid(row=0, column=0, columnspan=5, pady=10)

        # Default values are harmless and easy to edit
        self.hour_var = tk.StringVar(value="07")
        self.min_var = tk.StringVar(value="00")
        self.sec_var = tk.StringVar(value="00")

        # Entry styling to match the digital aesthetic
        entry_style = {
            'width': 4, 'font': ('Ubuntu', 24), 'justify': 'center',
            'bg': 'black', 'fg': '#00FF00', 'insertbackground': '#00FF00',
            'bd': 0, 'highlightthickness': 0
        }

        # Hour / minute / second entry widgets laid out horizontally
        self.hour_entry = tk.Entry(alarm_frame, textvariable=self.hour_var, **entry_style)
        self.hour_entry.grid(row=1, column=0, padx=10)

        tk.Label(alarm_frame, text=":", font=('Ubuntu', 24), fg='#00FF00', bg='black', bd=0, highlightthickness=0, relief='flat').grid(row=1, column=1)

        self.min_entry = tk.Entry(alarm_frame, textvariable=self.min_var, **entry_style)
        self.min_entry.grid(row=1, column=2, padx=10)

        tk.Label(alarm_frame, text=":", font=('Ubuntu', 24), fg='#00FF00', bg='black').grid(row=1, column=3)

        self.sec_entry = tk.Entry(alarm_frame, textvariable=self.sec_var, **entry_style)
        self.sec_entry.grid(row=1, column=4, padx=10)

        # The main action buttons (set alarm / stop alarm)
        button_style = {
            'font': ('Ubuntu', 18), 'bg': '#003300', 'fg': '#00FF00',
            'activebackground': '#006600', 'activeforeground': '#00FF00',
            'relief': 'raised', 'borderwidth': 3, 'padx': 20, 'pady': 10
        }

        self.set_alarm_btn = tk.Button(root, text="set alarm", command=self.set_alarm, **button_style)
        self.set_alarm_btn.pack(pady=20)

        # Stop button appears only while alarm is ringing
        self.stop_alarm_btn = tk.Button(
            root, text="stop alarm", command=self.stop_alarm,
            font=('Ubuntu', 18), bg='#330000', fg='#FF0000',
            activebackground='#660000', activeforeground='#FF0000',
            relief='raised', borderwidth=3, padx=20, pady=10
        )
        self.stop_alarm_btn.pack(pady=10)
        self.stop_alarm_btn.pack_forget()  # hidden until needed

        # Listbox showing active alarms with a scrollbar
        list_frame = tk.Frame(root, bg='black')
        list_frame.pack(pady=30, fill='both', expand=True)

        tk.Label(list_frame, text="active alarms", font=('Ubuntu', 20), fg='#00ff00', bg='black', bd=0, highlightthickness=0, relief='flat').pack()

        list_container = tk.Frame(list_frame, bg='black')
        list_container.pack(fill='both', expand=True, padx=100)

        self.alarms_listbox = tk.Listbox(
            list_container, height=8, font=('Ubuntu', 16),
            bg='black', fg='#00FF00', selectbackground='#006600', selectforeground='#00FF00'
        )
        self.alarms_listbox.pack(side='left', fill='both', expand=True)

        scrollbar = tk.Scrollbar(list_container, orient='vertical')
        scrollbar.pack(side='right', fill='y')
        self.alarms_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.alarms_listbox.yview)

        # Buttons to delete one or all alarms
        delete_frame = tk.Frame(list_frame, bg='black')
        delete_frame.pack(pady=15)

        self.delete_alarm_btn = tk.Button(
            delete_frame, text="delete alarm", command=self.delete_selected_alarm,
            font=('Ubuntu', 14), bg='#330000', fg='#FF0000', activebackground='#660000', activeforeground='#FF0000',
            padx=15, pady=8
        )
        self.delete_alarm_btn.pack(side='left', padx=10)

        self.delete_all_alarms_btn = tk.Button(
            delete_frame, text="delete all alarms", command=self.delete_all_alarms,
            font=('Ubuntu', 14), bg='#660000', fg='#FF0000', activebackground='#990000', activeforeground='#FF0000',
            padx=15, pady=8
        )
        self.delete_all_alarms_btn.pack(side='left', padx=10)

        # Keyboard shortcuts for convenience
        self.root.bind('<Escape>', self.exit_fullscreen)
        self.root.bind('<F11>', self.toggle_fullscreen)

        # Internal state for whether an alarm is currently ringing
        self.alarm_ringing = False

        # Start updating the clock label and the background alarm-check thread
        self.update_clock()
        self.check_alarm_thread = threading.Thread(target=self.check_alarm, daemon=True)
        self.check_alarm_thread.start()

    def exit_fullscreen(self, event=None):
        """Exit full screen and restore previous geometry."""
        if self.is_fullscreen:
            # Turn off the fullscreen attribute and restore size/position
            self.root.attributes('-fullscreen', False)
            try:
                self.root.geometry(self.previous_geometry)
            except Exception:
                # geometry restore is best-effort
                pass
            self.is_fullscreen = False

    def toggle_fullscreen(self, event=None):
        """Toggle full screen on/off. Save the previous geometry when entering full screen."""
        if not self.is_fullscreen:
            # Entering fullscreen: remember geometry so we can restore it later
            try:
                self.previous_geometry = self.root.geometry()
            except Exception:
                self.previous_geometry = None
            self.root.attributes('-fullscreen', True)
            self.is_fullscreen = True
        else:
            # Leaving fullscreen: restore geometry
            self.root.attributes('-fullscreen', False)
            if self.previous_geometry:
                try:
                    self.root.geometry(self.previous_geometry)
                except Exception:
                    pass
            self.is_fullscreen = False

    def toggle_time_format(self):
        """Toggle between 24-hour and 12-hour format"""
        self.time_format_24 = not self.time_format_24
        if self.time_format_24:
            self.format_btn.config(text="switch to 12H")
        else:
            self.format_btn.config(text="switch to 24H")
        self.update_alarms_list()

    def get_current_time(self):
        """Get current time in the selected format"""
        now = datetime.datetime.now()
        if self.time_format_24:
            return now.strftime("%H:%M:%S")
        else:
            return now.strftime("%I:%M:%S %p")

    def update_clock(self):
        current_time = self.get_current_time()
        self.time_label.config(text=current_time)
        
        # Optional: Add a blinking colon effect
        current_text = self.time_label.cget("text")
        if datetime.datetime.now().second % 2 == 0:
            # Replace colons with spaces for blinking effect
            blinking_text = current_text.replace(":", " ")
            self.time_label.config(text=blinking_text)
        else:
            self.time_label.config(text=current_time)
            
        self.root.after(1000, self.update_clock)

    def set_alarm(self):
        try:
            h = int(self.hour_var.get())
            m = int(self.min_var.get())
            s = int(self.sec_var.get())
            
            if 0 <= h < 24 and 0 <= m < 60 and 0 <= s < 60:
                alarm_time_24h = f"{h:02d}:{m:02d}:{s:02d}"
                
                # Check if alarm already exists
                for alarm in self.alarms:
                    if alarm['time_24h'] == alarm_time_24h and alarm['active']:
                        messagebox.showwarning("Duplicate Alarm", 
                                             f"Alarm for {self.format_alarm_time(alarm_time_24h)} already exists!")
                        return
                
                # Convert to display format
                display_time = self.format_alarm_time(alarm_time_24h)
                
                # Add alarm to list
                self.alarms.append({
                    'time_24h': alarm_time_24h,
                    'display': display_time,
                    'active': True
                })
                
                self.update_alarms_list()
                messagebox.showinfo("alarm set!!!", f"alarm set for {display_time}")
            else:
                messagebox.showerror("invalid!", "please enter a valid time (HH: 0-23, MM: 0-59, SS: 0-59).")
        except ValueError:
            messagebox.showerror("invalid!", "please enter numeric values")

    def format_alarm_time(self, time_24h):
        """Format alarm time based on current display format"""
        if self.time_format_24:
            return time_24h
        else:
            alarm_dt = datetime.datetime.strptime(time_24h, "%H:%M:%S")
            return alarm_dt.strftime("%I:%M:%S %p")

    def update_alarms_list(self):
        """Update the listbox with current alarms"""
        self.alarms_listbox.delete(0, tk.END)
        for i, alarm in enumerate(self.alarms):
            status = "ACTIVE" if alarm['active'] else "INACTIVE"
            display_text = f"{i+1:2d}. {alarm['display']} [{status}]"
            self.alarms_listbox.insert(tk.END, display_text)

    def delete_selected_alarm(self):
        """Delete the selected alarm"""
        selection = self.alarms_listbox.curselection()
        if selection:
            index = selection[0]
            alarm_time = self.alarms[index]['display']
            del self.alarms[index]
            self.update_alarms_list()
            messagebox.showinfo("alarm deleted")
        else:
            messagebox.showwarning("no selection", "please select an alarm to delete")

    def delete_all_alarms(self):
        """Delete all alarms"""
        if self.alarms:
            if messagebox.askyesno("delete all alarms", 
                                 "are you sure you want to delete ALL alarms????"):
                self.alarms.clear()
                self.update_alarms_list()
                messagebox.showinfo("alarms deleted", "all alarms have been deleted")
        else:
            messagebox.showinfo("no alarms", "there are no alarms to delete")

    def play_alarm_sound(self):
        """Play the alarm sound"""
        try:
            alarm_sound_path = "alarm_sound.mp3" # Path to your alarm sound file
            
            if os.path.exists(alarm_sound_path):
                pygame.mixer.music.load(alarm_sound_path)
                pygame.mixer.music.play(loops=-1)  # Loop indefinitely
            else:
                # Fallback: use system beep if MP3 file not found
                print(f"Alarm sound file not found at: {alarm_sound_path}")
                print("Using system beep instead.")
                def beep_loop():
                    while self.alarm_ringing:
                        try:
                            import winsound
                            winsound.Beep(1000, 500)
                            time.sleep(0.5)
                        except:
                            # If winsound not available, just sleep
                            time.sleep(1)
                threading.Thread(target=beep_loop, daemon=True).start()
                
        except Exception as e:
            print(f"Error playing alarm sound: {e}")

    def stop_alarm(self):
        """Stop the alarm sound"""
        self.alarm_ringing = False
        pygame.mixer.music.stop()
        self.stop_alarm_btn.pack_forget()
        self.set_alarm_btn.config(state='normal')

    def check_alarm(self):
        while True:
            current_time_24h = datetime.datetime.now().strftime("%H:%M:%S")
            
            for alarm in self.alarms:
                if alarm['active'] and alarm['time_24h'] == current_time_24h:
                    alarm['active'] = False  # Deactivate alarm
                    self.alarm_ringing = True
                    
                    # Update GUI in main thread
                    self.root.after(0, self.trigger_alarm_gui)
                    
                    # Play alarm sound in a separate thread
                    sound_thread = threading.Thread(target=self.play_alarm_sound, daemon=True)
                    sound_thread.start()
                    
                    # Show alert message (this will block until user clicks OK)
                    messagebox.showinfo("Alarm", "Time's up!")
                    
                    # Auto-stop alarm when user clicks OK
                    self.stop_alarm()
                    self.update_alarms_list()
                    
            time.sleep(1)

    def trigger_alarm_gui(self):
        """Update GUI when alarm triggers (must be called from main thread)"""
        self.stop_alarm_btn.pack(pady=5)
        self.set_alarm_btn.config(state='disabled')

if __name__ == "__main__":
    root = tk.Tk()
    app = DigitalClock(root)
    root.mainloop()