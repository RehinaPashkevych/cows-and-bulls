import os
import time
from datetime import datetime
from random import randint
from tkinter import *
from tkinter import ttk, font
from PIL import Image, ImageTk
import pygame
from tkdnd import TkinterDnD
from records_window import display_records_window  # Import the function
import json

PHOTO_SCALE = 60
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 450
GIF_DELAY = 100

num_wins = 0
num_losses = 0
bull_scale = 1  # Initial scale for the bull image
cow_scale = 1  # Initial scale for the cow image

entry_vars = []
entry_fields = []
main_screen_objects = []

root = TkinterDnD.Tk()
root.title("Cows and Bulls")
root.config(bg="white")
root.geometry(str(SCREEN_WIDTH) + "x" + str(SCREEN_HEIGHT))

pygame.init()
pygame.mixer.init()

canvas_win = None
canvas_text_score = None
error_label = None
start_game_time = None
win_sound = None

is_on_win_screen = False
is_game_paused = False

errmsg = StringVar()
winsmsg = StringVar()
lossesmsg = StringVar()
username_var = StringVar()

paused_time = 0

menu_records = None
menu_settings = None
menu_help = None
menu_exit = None
prompt_username = None
restart_button_text = None
pause_button_text = None
resume_button_text = None
label_time = None
message_correct_guess = None
message_not_a_match = None
message_enter_single_digit = None
message_enter_valid_integer = None
message_game_paused = None
message_game_rules = None
message_license = None
menu_settings_music = None
menu_settings_music_checkbox = None
menu_settings_sound_style = None
menu_settings_language = None
menu_settings_save = None
message_enter_between = None
message_you_win = None
message_your_score = None

language_files = {
    "English": "en.json",
    "Polish": "pl.json",
    "Ukrainian": "ua.json",
    "Spanish": "es.json",
}

selected_language = "English"


def extract_translation_variables(translations):
    for key, value in translations.items():
        globals()[key] = value


def load_translations(language_file):
    try:
        with open(f'materials/languages/{language_file}', 'r', encoding='utf-8') as json_file:
            translations = json.load(json_file)
            return translations
    except FileNotFoundError:
        return {}  # Return an empty dictionary if the language file doesn't exist


def open_help():
    # Create a new Toplevel window for the help
    help_window = Toplevel()
    help_window.title("Game Rules and License")

    # Configure the style for the help window
    help_style = ttk.Style()
    help_style.configure("Help.TLabel", foreground="black", background="white", font=("Arial", 14))
    help_style.configure("License.TLabel", foreground="black", background="white", font=("Arial", 12))

    # Create a label with the game rules and apply a different font and style
    rules_text = message_game_rules

    help_label = ttk.Label(help_window, text=rules_text, style="Help.TLabel")
    help_label.pack(padx=10, pady=10)

    # Add a "License" section with license information
    license_text = message_license

    license_label = ttk.Label(help_window, text=license_text, style="License.TLabel")
    license_label.pack(padx=2, pady=5)

    # Center the help window on the screen
    help_window.geometry("+{}+{}".format(
        root.winfo_x() + (root.winfo_width() // 2 - help_window.winfo_reqwidth() // 2),
        root.winfo_y() + (root.winfo_height() // 2 - help_window.winfo_reqheight() // 2)
    ))


def open_records():
    display_records_window()


def update_language(language):
    global  selected_language

    if language in language_files:
        selected_language = language
        language_file = language_files[language]
        translations = load_translations(language_file)
        extract_translation_variables(translations)
        print(language_file)
    else:
        print(f"Language '{language}' is not supported.")


update_language(selected_language)


def save_settings():
    global music_enabled_var, sound_style_var, language_var, selected_language, settings_window

    # Save the selected settings to a file or apply them in your application
    music_enabled = music_enabled_var.get()
    sound_style = sound_style_var.get()
    selected_language = language_var.get()
    # Update the language based on the user's choice
    update_language(selected_language)
    update_ui_language()
    settings_window.destroy()


def open_settings():
    global music_enabled_var, sound_style_var, language_var, selected_language, settings_window
    settings_window = Toplevel()
    settings_window.title(menu_settings)

    music_enabled_label = Label(settings_window, text=menu_settings_music, font=("Arial", 12))
    music_enabled_label.grid(row=0, column=0, padx=10, pady=5)

    music_enabled_var = IntVar()
    music_checkbox = Checkbutton(settings_window, text=menu_settings_music_checkbox, variable=music_enabled_var,
                                 font=("Arial", 12))
    music_checkbox.grid(row=0, column=1)

    sound_style_label = Label(settings_window, text=menu_settings_sound_style, font=("Arial", 12))
    sound_style_label.grid(row=1, column=0, padx=10, pady=5)

    sound_style_var = StringVar()
    sound_style_combobox = ttk.Combobox(settings_window, textvariable=sound_style_var,
                                        values=["Style 1", "Style 2", "Style 3"], font=("Arial", 12))
    sound_style_combobox.grid(row=1, column=1)

    language_label = Label(settings_window, text=menu_settings_language, font=("Arial", 12))
    language_label.grid(row=2, column=0, padx=10, pady=5)

    language_var = StringVar()
    language_combobox = ttk.Combobox(
        settings_window, textvariable=language_var, values=list(language_files.keys()), font=("Arial", 12)
    )
    language_combobox.grid(row=2, column=1)

    language_var.set(selected_language)
    #language_combobox.bind("<<ComboboxSelected>>", update_ui_language)


    save_button = Button(settings_window, text=menu_settings_save, command=save_settings, font=("Arial", 12))
    save_button.grid(row=3, columnspan=2, pady=10)


def update_ui_language():
    global main_menu
    username_label.config(text=f"{prompt_username}: {current_username}")
    restart_button.config(text=restart_button_text)
    pause_button.config(text=pause_button_text)
    main_menu.entryconfig(1, label=menu_records, command=open_records)
    main_menu.entryconfig(2, label=menu_settings, command=open_settings)
    main_menu.entryconfig(3, label=menu_help, command=open_help)
    main_menu.entryconfig(4, label=menu_exit, command=exit_app)


def exit_app():
    root.quit()


def get_last_username():
    try:
        with open("records.txt", "r") as records_file:
            lines = records_file.readlines()
            if lines:
                last_line = lines[-1].strip()
                parts = last_line.split(", ")
                for part in parts:
                    if part.startswith("Username: "):
                        return part.replace("Username: ", "")
    except FileNotFoundError:
        pass
    return "Cool Name"


# Set the initial current_username


def create_main_screen():
    global entry_vars, entry_fields, main_screen_objects, canvas_bull, \
        image_bull, canvas_cow, image_cow, error_label, win_sound, \
        happy_girl_sound, is_game_paused, paused_time, start_time, pause_button, timer_label, \
        start_game_time, current_username, username_var, restart_button, pause_button_text, username_label, restart_button_text

    win_sound = pygame.mixer.Sound("materials/audio/win.mp3")
    happy_girl_sound = pygame.mixer.Sound("materials/audio/happy-girl.mp3")

    font1 = font.Font(family="Arial", size=20, weight="normal", slant="roman")
    font_label = font.Font(family="Arial", size=14, weight="normal", slant="roman")
    font_label_10 = font.Font(family="Arial", size=10, weight="normal", slant="roman")

    entry_vars = []
    entry_fields = []
    main_screen_objects = []

    # Initialize the timer_id variable
    timer_id = None
    start_time = time.time()
    start_game_time = datetime.now()  # Store the game start time
    current_username = get_last_username()

    for i in range(4):
        # ENTRIES ------------------------------
        var = StringVar()
        entry_var = ttk.Entry(
            textvariable=var, validate="key",
            validatecommand=(root.register(is_valid), "%P", i),
            font=font1, width=3
        )
        entry_var.grid(row=1, column=i, padx=25, pady=230)
        entry_vars.append(var)
        entry_fields.append(entry_var)
        main_screen_objects.append(entry_var)

    def update_username(event=None):
        global current_username, username_label
        new_username = username_entry.get()
        current_username = new_username
        username_label.config(text=f"{prompt_username}: {current_username}")
        username_label.place(x=100, y=0)
        username_entry.place_forget()

    def switch_to_entry(event):
        global username_label
        username_label.place_forget()
        username_entry.place(x=100, y=0)
        username_entry.focus_set()

    username_label = Label(root, foreground="black", text=f"{prompt_username}: {current_username}", font=font_label_10,
                           background="white", borderwidth=2, relief="ridge", )
    username_label.place(x=100, y=0)
    username_label.bind("<Button-1>", switch_to_entry)

    username_entry = Entry(root, font=font_label_10, width=15)
    username_entry.bind('<Return>', update_username)
    username_entry.bind("<FocusOut>", update_username)

    # BUTTONS --------------------------------------------------------

    restart_button = Button(text=restart_button_text, command=restart_game, background="lightskyblue")
    restart_button.place(x=SCREEN_WIDTH / 2, y=SCREEN_HEIGHT - 40)

    def toggle_pause():
        global is_game_paused, start_time, paused_time, pause_button, pause_button_text, resume_button
        if is_game_paused:
            # Resume the game timer
            is_game_paused = False
            pause_button.config(text=pause_button_text)
            start_time = time.time() - paused_time

            for i in range(4):
                # checking the entries after pause to freeze needed
                entry_value = entry_fields[i].get()
                if entry_value.isdigit():  # Check if it's a valid integer string
                    entry_value = int(entry_value)
                    if entry_value == random_values[i]:
                        entry_fields[i].config(state="readonly")
                    else:
                        entry_fields[i].config(state="normal")
                else:
                    entry_fields[i].config(state="normal")

            # Update the timer immediately
            update_timer()
        else:
            pause_button.config(text=resume_button_text)
            is_game_paused = True
            paused_time = time.time() - start_time
            for entry_field in entry_fields:
                entry_field.config(state="readonly")
            if timer_id is not None:
                root.after_cancel(timer_id)

    pause_button = Button(text=pause_button_text, command=toggle_pause, background="lightcoral")
    pause_button.place(x=SCREEN_WIDTH / 2 - 70, y=SCREEN_HEIGHT - 40)
    main_screen_objects.append(pause_button)

    # CANVAS with IMAGES -----------------------------

    canvas_bull = Canvas(bg="white", width=PHOTO_SCALE, height=PHOTO_SCALE, highlightthickness=0, relief='ridge')
    canvas_bull.place(x=150, y=130)
    main_screen_objects.append(canvas_bull)

    image_bull = Image.open("materials/Optimized-bull2.PNG").resize((PHOTO_SCALE, PHOTO_SCALE))
    image_bull = ImageTk.PhotoImage(image_bull)
    canvas_bull.create_image(0, 0, image=image_bull, anchor=NW)

    canvas_cow = Canvas(bg="white", width=PHOTO_SCALE, height=PHOTO_SCALE, highlightthickness=0, relief='ridge')
    canvas_cow.place(in_=root, x=150, y=30)
    main_screen_objects.append(canvas_cow)

    image_cow = Image.open("materials/Optimized-cow.PNG").resize((PHOTO_SCALE, PHOTO_SCALE))
    image_cow = ImageTk.PhotoImage(image_cow)
    canvas_cow.create_image(0, 0, image=image_cow, anchor=NW)

    # LABELS--------------------------------

    winsmsg.set("Cows: 0")
    lossesmsg.set("Bulls: 0")

    error_label = ttk.Label(foreground="red", textvariable=errmsg, font=font_label, background="white")
    error_label.place(x=60, y=300)
    main_screen_objects.append(error_label)

    num_wins_label = ttk.Label(foreground="black", textvariable=winsmsg, font=font_label, background="white")
    num_wins_label.place(x=60, y=50)
    main_screen_objects.append(num_wins_label)

    num_losses_label = ttk.Label(foreground="black", textvariable=lossesmsg, font=font_label, background="white")
    num_losses_label.place(x=60, y=150)
    main_screen_objects.append(num_losses_label)

    # Add a label to display the timer
    timer_label = ttk.Label(foreground="black", text="Time: 0:00", font=font_label_10, background="white",
                            borderwidth=2,
                            relief="ridge", )
    timer_label.place(x=293, y=0)
    main_screen_objects.append(timer_label)

    update_timer()


def update_timer():
    global start_time, timer_label, timer_id
    if not is_game_paused:
        current_time = time.time() - start_time
        minutes, seconds = divmod(int(current_time), 60)
        timer_label.config(text=f"{label_time}: {minutes}:{seconds:02}")
        # Continue updating the timer
        timer_id = root.after(1000, update_timer)


def restart_game():
    global num_wins, num_losses, random_values, start_time, current_time, \
        paused_time, is_game_paused, pause_button, is_on_win_screen, win_sound, \
        start_game_time, current_username, username_var

    win_sound.stop()

    num_wins = 0
    num_losses = 0
    current_time = 0
    paused_time = 0
    start_time = time.time()
    start_game_time = datetime.now()  # Update the game start time
    random_values = [randint(0, 9) for _ in range(4)]
    print(random_values)

    # Clear the entry fields
    for entry_field in entry_fields:
        entry_field.config(state="normal")
        entry_field.delete(0, "end")

    # Reset labels
    winsmsg.set("Cows: 0")
    lossesmsg.set("Bulls: 0")
    errmsg.set("")

    if is_on_win_screen:
        canvas_win.place_forget()
        canvas_text_score.place_forget()
        is_on_win_screen = False
        create_main_screen()
    if is_game_paused:
        is_game_paused = False
        pause_button.config(text={pause_button})
        # Update the timer label to display "Time: 0:00"
    timer_label.config(text="Time: 0:00")
    # Update the timer immediately
    update_timer()


def enlarge_bull():
    global bull_scale
    bull_scale = 2
    update_bull_image()
    root.after(1000, reset_bull_scale)  # Schedule the reset after 2 seconds


def enlarge_cow():
    global cow_scale
    cow_scale = 2
    canvas_cow.place(in_=root, x=150, y=30)
    update_cow_image()
    root.after(1000, reset_cow_scale)  # Schedule the reset after 2 seconds


def reset_bull_scale():
    global bull_scale
    bull_scale = 1
    update_bull_image()


def reset_cow_scale():
    global cow_scale
    cow_scale = 1
    update_cow_image()


def update_bull_image():
    global bull_scale
    canvas_bull.config(width=PHOTO_SCALE * bull_scale, height=PHOTO_SCALE * bull_scale)
    image = Image.open("materials/Optimized-bull2.PNG").resize((PHOTO_SCALE * bull_scale, PHOTO_SCALE * bull_scale))
    image = ImageTk.PhotoImage(image)
    canvas_bull.create_image(0, 0, image=image, anchor=NW)
    canvas_bull.image = image  # Keep a reference to the image to prevent it from being garbage collected


def update_cow_image():
    global cow_scale
    canvas_cow.config(width=PHOTO_SCALE * cow_scale, height=PHOTO_SCALE * cow_scale)
    image = Image.open("materials/Optimized-cow.PNG").resize((PHOTO_SCALE * cow_scale, PHOTO_SCALE * cow_scale))
    image = ImageTk.PhotoImage(image)
    canvas_cow.create_image(0, 0, image=image, anchor=NW)
    canvas_cow.image = image  # Keep a reference to the image to prevent it from being garbage collected


def display_image_sequence(window, image_folder):
    image_files = sorted(
        [os.path.join(image_folder, filename) for filename in os.listdir(image_folder) if filename.endswith(".png")])
    num_images = len(image_files)

    def update_label(index):
        nonlocal label
        image = Image.open(image_files[index % num_images]).resize((SCREEN_WIDTH, SCREEN_HEIGHT))
        photo = ImageTk.PhotoImage(image)
        label.config(image=photo)
        label.image = photo  # Keep a reference to prevent garbage collection
        window.after(100, update_label, (index + 1) % num_images)

    label = Label(window)
    label.place(x=0, y=0)

    update_label(0)


def is_valid(new_val, entry_idx):
    try:
        global num_wins, num_losses, happy_girl_sound
        new_val = new_val.replace(" ", "")
        integer_value = int(new_val)
        if is_game_paused:
            # The game is paused, so don't allow guesses
            errmsg.set("Game is paused.")
        if 0 <= integer_value <= 9 and len(new_val) == 1:
            if integer_value == random_values[int(entry_idx)]:
                error_label.config(foreground="green")
                entry_fields[int(entry_idx)].config(state="readonly")
                errmsg.set(message_correct_guess)
                num_wins += 1
                winsmsg.set("Cows: " + str(num_wins))
                enlarge_cow()
                happy_girl_sound.play()
                if num_wins == 4:
                    show_win_screen()
            else:
                num_losses += 1
                error_label.config(foreground="red")
                errmsg.set(message_not_a_match)
                lossesmsg.set("Bulls: " + str(num_losses))
                enlarge_bull()
        elif len(new_val) != 1:
            # num_losses += 1
            error_label.config(foreground="red")
            errmsg.set(message_enter_single_digit)
            lossesmsg.set("Bulls: " + str(num_losses))
        else:
            # num_losses += 1
            error_label.config(foreground="red")
            errmsg.set(message_enter_between)
            lossesmsg.set("Bulls: " + str(num_losses))
    except ValueError:
        error_label.config(foreground="red")
        errmsg.set(message_enter_valid_integer)
    return True


def show_win_screen():
    global restart_button, canvas_win, is_on_win_screen, canvas_text_score, win_sound, \
        start_game_time, current_username

    end_time = datetime.now()  # Store the game end time
    elapsed_time = end_time - start_game_time  # Calculate the elapsed time
    formatted_end_time = end_time.strftime("%d.%m.%Y")  # Format the end time as "dd.mm.yyyy"

    # Write game results (number of bulls, time, and date) to the "records.txt" file
    with open("records.txt", "a") as records_file:
        records_file.write(
            f"Username: {current_username}, Bulls: {num_losses}, Time: {elapsed_time}, Date: {formatted_end_time}\n")

    is_on_win_screen = True

    win_sound.play()

    # Hide the entries and labels
    for object_main_screen in main_screen_objects:
        object_main_screen.grid_forget()
        object_main_screen.place_forget()

    canvas_win = Canvas(bg="white", width=SCREEN_WIDTH, height=SCREEN_HEIGHT, highlightthickness=0,
                        relief='ridge')
    canvas_win.place(x=0, y=0)
    display_image_sequence(canvas_win, "materials/cow-gif")

    restart_button = Button(canvas_win, text=restart_button_text, command=restart_game, background="lightskyblue")
    canvas_win.create_window(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 40, window=restart_button)

    canvas_text_score = Canvas(bg="gray97", width=SCREEN_WIDTH - 30, height=SCREEN_HEIGHT / 4 - 50,
                               highlightthickness=0, relief='ridge')
    canvas_text_score.create_text(
        160, 40,  # Center the text
        text=f"{message_you_win}\n{message_your_score} Cows: {num_wins}, Bulls: {num_losses}",
        font=("Arial", 16),
        fill="black"
    )
    canvas_text_score.place(x=20, y=20)


random_values = [randint(0, 9) for _ in range(4)]
print(random_values)

# Create a themed menu
main_menu = Menu(root)
root.config(menu=main_menu)

main_menu.add_command(label=menu_records, command=open_records)
main_menu.add_command(label=menu_settings, command=open_settings)
main_menu.add_command(label=menu_help, command=open_help)
main_menu.add_command(label=menu_exit, command=exit_app)


create_main_screen()

root.config(menu=main_menu)
root.mainloop()
