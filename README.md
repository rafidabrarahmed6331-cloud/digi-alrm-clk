# digi-alrm-clk

digi-alarm clock

A feature-rich digital clock and alarm application built with Python's Tkinter library. It features a clean, retro-inspired interface with a green-on-black "digital" display, along with robust alarm management functionalities.

![alt text](http://url/to/img.png)

Features

    Large, Readable Display: Shows the current time in a bold, digital-style font that is easy to read from a distance.

    Togglable Time Format: Easily switch between 24-hour and 12-hour (AM/PM) time formats with a single button click.

    Multiple Alarms: Set multiple alarms with precision to the hour, minute, and second.

    Alarm Management: A clear listbox displays all active alarms. You can delete a selected alarm or clear all alarms at once.

    Audible Alerts: Plays a sound when an alarm goes off. It looks for an alarm_sound.mp3 file but includes a system beep as a fallback.

    Fullscreen Mode: Press F11 to enter an immersive, distraction-free fullscreen mode. Press Escape to return to the windowed view.

    Non-Blocking Alarms: Uses threading to ensure the GUI remains responsive while the application continuously checks for pending alarms in the background.

    Visual Feedback:

        The colon on the clock display blinks every second.

        A "Stop Alarm" button appears only when an alarm is ringing.

Prerequisites

First ensure you have the following installed on your system:

    Python 3.x

    pip (Python's package installer)

Installation & Setup:

You can follow these steps to get the digital clock up and running.

    Clone the Repository
    Bash

git clone <your-repository-url>
cd <repository-directory>

Install Dependencies: This project requires the pygame library to play the alarm sound. You can install it using pip:
Bash

pip install pygame

Alternatively, for easier dependency management, you can create a requirements.txt file containing the line pygame and install from it:
Bash

    pip install -r requirements.txt

    Add an Alarm Sound (Optional but Recommended). For the best experience, place an MP3 audio file named alarm_sound.mp3 in the same directory as the digi_clk.py script. If the application cannot find this file, it will fall back to using system beeps.

How to Use

    Run the Application Execute the script from your terminal:
    Bash

    python digi_clk.py

    Setting an Alarm

        Enter the desired hour (0-23), minute (0-59), and second (0-59) in the input boxes.

        Click the "set alarm" button.

        A confirmation message will appear, and the alarm will be added to the "active alarms" list.

    Managing Alarms

        To delete a specific alarm, click on it in the listbox to select it, then click the "delete alarm" button.

        To delete all alarms at once, click the "delete all alarms" button and confirm your choice.

    When an Alarm Goes Off

        The alarm sound will play on a loop.

        A "stop alarm" button will appear. Click it to silence the sound.

        The alarm will be automatically deactivated in the list.

Keyboard Shortcuts

    F11: Toggle fullscreen mode.

    Escape: Exit full-screen mode.
