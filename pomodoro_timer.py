import tkinter as tk
from tkinter import ttk
from playsound import playsound

class WindowMain(tk.Tk):
    """
    root window class. holds raise_window(). other window classes established in WindowMain.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.columnconfigure(0, weight=1)
        self.title("Pomodoro Timer")
        style = ttk.Style(self) #must pass 'style' into other classes

        container = ttk.Frame(self)
        container.grid(row=0, column=0, sticky="NSEW")

        timer = Timer(container, self, style) #initialize the Timer window
        timer.grid(row=0, column=0, sticky="NSEW")

        settings = Settings(container, timer, self, style) #init Settings window. must pass Timer class in to access variables.
        settings.grid(row=0, column=0, sticky="NSEW")

        self.windows = {Timer:timer, Settings:settings} #create a dict to use raise_window(). a list wont work.

        self.raise_window(Timer)

    def raise_window(self, WindowClass):
        """
        raises the window of choice
        """
        window = self.windows[WindowClass]
        window.tkraise()

class Timer(ttk.Frame):
    """
    class for the timer page. holds most of the functionality.
    """
    def __init__(self, container, controller, style, *args, **kwargs):
        super().__init__(container, *args, **kwargs)

        self.columnconfigure(0, weight=1)

        self.setting_times = [] #holds a list of times that spinboxes use to set times.
        self.create_time_values() #func that creates populates settings_times.
        #init settings variables
        self.flow_time_setting = tk.StringVar(value=self.setting_times[25])
        self.break_time_setting = tk.StringVar(value=self.setting_times[5])
        self.long_break_time_setting = tk.StringVar(value=self.setting_times[30])
        self.auto_start_setting = tk.IntVar(value=1)
        self.long_break_setting = tk.IntVar(value=4)
        self.flow_count = tk.IntVar(value=0)
        #init timer variables
        self.timer_mode_list = ["flow", "break", "long break"]
        self.timer_time = tk.StringVar(value=self.flow_time_setting.get()) #countdown time displayed
        self.timer_mode = tk.StringVar(value=self.timer_mode_list[0]) #mode of the timer, default = "flow"
        self.timer_running = False
        #init misc variables
        self.start_button_name_list = ["Start", "Pause"] #holds names for start button label
        self.start_button_name = tk.StringVar(value=self.start_button_name_list[0]) #var that actually sets start button display
        self.flow_count_progress = tk.StringVar(value="0/4") #counts number of flows completed

        #styles
        print(style.element_options("Label.label"))
        print(style.element_options("Label.padding"))
        style.configure("TimerButton.TButton", font=("IBM Plex Sans Condensed", 12))
        style.configure("TimerLabel.TLabel", font=("IBM Plex Sans Medium", 25))
        style.configure("TimerNumLabel.TLabel", font=("IBM Plex Mono Medium", 18))
        style.configure("TimerNum.TLabel", font=("IBM Plex Mono Medium", 55))

        #frame that holds all buttons that control timer, sits above timer in root.container.timer
        frame_for_buttons = ttk.Frame(self)
        frame_for_buttons.grid(row=0, column=0, sticky="EW", padx=20, pady=(10,0))

        self.button_width = 8
        start_pause_button = ttk.Button(
            frame_for_buttons,
            width=self.button_width,
            textvariable=self.start_button_name,
            command=self.start_button_func)
        restart_button = ttk.Button(
            frame_for_buttons,
            width=self.button_width,
            text="Restart",
            command=self.restart_button_func)
        skip_button = ttk.Button(
            frame_for_buttons,
            width=self.button_width,
            text="Skip",
            command=lambda: self.change_timer_mode(True))
        settings_button = ttk.Button(
            frame_for_buttons,
            width=self.button_width,
            text="Settings",
            command=lambda: controller.raise_window(Settings))

        start_pause_button.grid(row=0, column=0, padx=2)
        restart_button.grid(row=0, column=1, padx=2)
        skip_button.grid(row=0, column=2, padx=2)
        settings_button.grid(row=0, column=3, padx=2)

        #frame for timer that holds timer and associated widgets, sits below buttons in root.container.timer
        frame_for_timer = tk.Frame(self)
        frame_for_timer.grid(row=1, column=0, sticky="EW")
        frame_for_timer.columnconfigure(0, weight=1)

        #widgets on timer page
        countdown_timer_label = ttk.Label(
            frame_for_timer,
            style="TimerLabel.TLabel",
            textvariable=self.timer_mode)
        countdown_timer = ttk.Label(
            frame_for_timer,
            style="TimerNum.TLabel",
            textvariable=self.timer_time)
        flow_count_label = ttk.Label(
            frame_for_timer,
            style="TimerNumLabel.TLabel",
            textvariable=self.flow_count_progress)

        countdown_timer.grid(row=1, column=0)
        countdown_timer_label.grid(row=0, column=0, pady=(20,0))
        flow_count_label.grid(row=2, column=0, pady=(0,20))

        for button in (start_pause_button, restart_button, skip_button, settings_button):
            button["style"] = "TimerButton.TButton"

    def start_button_func(self):
        """
        func for start_pause_button.
        - switches timer_running, changes name of the button, and then calls decrement_time()
        """
        if self.timer_running:
            self.timer_running = False
            self.start_button_name.set(self.start_button_name_list[0])
        else:
            self.timer_running = True
            self.start_button_name.set(self.start_button_name_list[1])

        self.decrement_time()

    def decrement_time(self):
        """
        func that controls timer countdown.
        - .gets() the timer_time and subtracts 1 second per function call.
        - .sets() the timer_time to the new time and calls decrement_time() again
        - this loops proceeds as long as timer_running == True or until the timer_time == 00:00. auto_start setting controls whether it continues past this automatically.
        """
        time_left = self.timer_time.get()
        auto_start = self.auto_start_setting.get()
        minutes, seconds = time_left.split(":")

        minutes, seconds = int(minutes), int(seconds)

        if self.timer_running and time_left != "00:00":

            if seconds > 0:
                seconds = seconds - 1
            else:
                minutes = minutes - 1
                seconds = 59

            self.timer_time.set(f"{minutes:02d}:{seconds:02d}")
            self.after(1000, self.decrement_time)

        elif (self.timer_running) and (time_left=="00:00"):

            playsound('/Users/sailormetz/Python/Scratch/Pomodoro_Timer/flute_alarm.wav') #play sound when timer_time reaches 0

            #check auto_start setting
            if auto_start==1:
                self.change_timer_mode(False) #changes mode and automatically starts
                self.after(1000, self.decrement_time)

            elif auto_start==0:
                #changes mode, sets timer_running to false to decrement, resumes when start button is pushed again.
                self.change_timer_mode(False)
                self.timer_running = False #stops decrement_time() from being called automatically
                self.start_button_name.set(self.start_button_name_list[0])

    def change_timer_mode(self, skip_boolean):
        """
        changes timer_mode to either flow, break, or long break. sets all variables accordingly. increments the flow_count.
        - takes one argument, skip_boolean as T/F, which should be True when this func is used in the skip_button, and False when called anywhere else.
        """
        if skip_boolean == True: #pauses timer so that mode change happens without calling decrement_time()
            self.timer_running = False
            self.start_button_name.set(self.start_button_name_list[0])

        mode = self.timer_mode.get() #get current timer_mode

        if mode=="flow":

            self.update_flow_count(False) #call update_flow_count() since flow completed

            if self.flow_count.get() == 4: #enter long break timer_mode.
                self.timer_mode.set(self.timer_mode_list[2])
                self.timer_time.set(self.long_break_time_setting.get()) #set timer_time to whatever long_break_time_setting is
            else: #enter break timer_mode
                self.timer_mode.set(self.timer_mode_list[1])
                self.timer_time.set(self.break_time_setting.get()) #set timer_time to break_time_setting

        elif mode=="break": #enter flow timer_mode
            self.timer_mode.set(self.timer_mode_list[0])
            self.timer_time.set(self.flow_time_setting.get()) #set timer_time to flow_time_setting

        elif mode=="long break": #enter flow timer_mode
            self.timer_mode.set(self.timer_mode_list[0])
            self.timer_time.set(self.flow_time_setting.get())
            self.update_flow_count(True) #calls update_flow_count with restart=True, which resets flow_count and flow_count_progress

    def restart_button_func(self):
        """
        1. stop the timer
        2. reset the timer to flow
        3. change button names accordingly
        """
        self.timer_running = False
        self.timer_mode.set(self.timer_mode_list[0])
        self.timer_time.set(self.flow_time_setting.get()) #connect to settings var eventually
        self.start_button_name.set(self.start_button_name_list[0])
        self.update_flow_count(True) #restart=True which resets flow_count and flow_count_progress

    def update_timer_time(self, mode):
        """
        used in the time settings spinboxes to update the timer_time after changing any of the settings. checks for the mode to set the timer_time while the timer is running. Otherwise any changes made to the timer_settings wont take effect until change_timer_mode() is called. However, we want to be able to change the timer while still running, so this func automatically .sets() timer_time to the affected setting if the setting matches the current mode.
        """

        current_mode = self.timer_mode.get()

        if mode == current_mode:

            if mode == "flow":
                self.timer_time.set(self.flow_time_setting.get())

            elif mode == "break":
                self.timer_time.set(self.break_time_setting.get())

            elif mode == "long break":
                self.timer_time.set(self.long_break_time_setting.get())

    def create_time_values(self):
        """
        used at Timer init to create the time settings
        """

        for i in range(0, 61):
            if len(str(i)) == 1:
                self.setting_times.append("0" + str(i) + ":00")
            else:
                self.setting_times.append(str(i) + ":00")

    def update_flow_count(self, restart):
        """
        updates the flow count or resets the flow count as well as the flow_count_progress message
        - takes one parameter, restart, as either T/F. Use True when at the end of "long break" timer_mode and for restart_button_func. Use False in all other scenarios.
        """

        if restart == True:
            self.flow_count.set(0)
            self.flow_count_progress.set("0/4")
            return

        else:
            self.flow_count.set(self.flow_count.get()+1)
            flow_count = self.flow_count.get()
            msg = str(flow_count) + "/4"
            self.flow_count_progress.set(msg)

class Settings(ttk.Frame):
    """
    class for the Settings page.
    parameters:
    container = container in the WindowMain class.
    timer = Timer class - for access to timer instance funcs, variables
    controller = WindowMain - for access to WindowMain instance funcs, variables
    style = ttk.Style(root) - for styling
    """
    def __init__(self, container, timer, controller, style, *args, **kwargs):
        super().__init__(container, *args, **kwargs)

        self.columnconfigure(0, weight=1)

        style.configure("SettingsLabel.TLabel", font=("IBM Plex Sans Medium", 17))
        style.configure("SettingsSpin.TSpinbox", font=("IBM Plex Mono", 13))

        #frame for settings buttons
        frame_for_settings = ttk.Frame(self)
        frame_for_settings.grid(row=1, column=0)
        frame_for_settings.columnconfigure((0), weight=6)
        frame_for_settings.columnconfigure((1), weight=1)

        #frame for just the back button
        frame_for_back_button = ttk.Frame(self)
        frame_for_back_button.grid(row=0, column=0, sticky="E")

        #frame that holds the radio buttons inside of frame_for_settings
        frame_for_radios = ttk.Frame(frame_for_settings)
        frame_for_radios.grid(row=4, column=1, sticky="NSEW")

        back_button = ttk.Button(
            frame_for_back_button,
            text="Back",
            style="TimerButton.TButton",
            command=lambda: controller.raise_window(Timer))

        #time setting label and spinbox pairs
        entry_width = 8
        flow_setting_label = ttk.Label(frame_for_settings, text="Flow")
        flow_setting_entry = ttk.Spinbox(
            frame_for_settings,
            width = entry_width,
            values = timer.setting_times,
            wrap = True,
            textvariable = timer.flow_time_setting,
            command = lambda: timer.update_timer_time(mode="flow"))

        break_setting_label = ttk.Label(frame_for_settings, text="Break")
        break_setting_entry = ttk.Spinbox(
            frame_for_settings,
            width = entry_width,
            values = timer.setting_times,
            wrap = True,
            textvariable = timer.break_time_setting,
            command = lambda: timer.update_timer_time(mode="break"))

        long_break_setting_label = ttk.Label(frame_for_settings, text="Long Break")
        long_break_setting_entry = ttk.Spinbox(
            frame_for_settings,
            width = entry_width,
            values = timer.setting_times,
            wrap = True,
            textvariable = timer.long_break_time_setting,
            command = lambda: timer.update_timer_time(mode="long break"))

        auto_start_button_label = ttk.Label(frame_for_settings, text="Auto Start")
        auto_button_one = ttk.Radiobutton(
            frame_for_radios,
            text="Yes",
            variable=timer.auto_start_setting,
            value=1)

        auto_button_two = ttk.Radiobutton(
            frame_for_radios,
            text="No",
            variable=timer.auto_start_setting,
            value=0)

        back_button.grid(row=0, column=0, padx=(20), pady=(10,10))
        label_sticky = "W"
        #labels
        flow_setting_label.grid(row=1, column=0, sticky=label_sticky)
        break_setting_label.grid(row=2, column=0, sticky=label_sticky)
        long_break_setting_label.grid(row=3, column=0, sticky=label_sticky)
        auto_start_button_label.grid(row=4, column=0, sticky=label_sticky)


        entry_sticky = "W"
        entry_span = 1
        entry_pad = (15,0)
        entry_ipad = 2
        #entries and buttons
        flow_setting_entry.grid(row=1, column=1, columnspan=entry_span, sticky=entry_sticky, padx=entry_pad, ipady=entry_ipad)
        break_setting_entry.grid(row=2, column=1, columnspan=entry_span, sticky=entry_sticky, padx=entry_pad, ipady=entry_ipad)
        long_break_setting_entry.grid(row=3, column=1, columnspan=entry_span, sticky=entry_sticky, padx=entry_pad, ipady=entry_ipad)
        auto_button_one.grid(row=0, column=0, sticky="W", padx=entry_pad, ipady=entry_ipad)
        auto_button_two.grid(row=0, column=1, sticky="E", padx=entry_pad, ipady=entry_ipad)

        for label in (flow_setting_label,break_setting_label, long_break_setting_label, auto_start_button_label):
            label["style"] = "SettingsLabel.TLabel"

#start main logic
root = WindowMain()

root.mainloop()
