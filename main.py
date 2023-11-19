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
music_enabled_var = StringVar()
sound_enabled_var = StringVar()
sound_style_var = StringVar()

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
menu_settings_sound_checkbox = None
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
selected_style = "maincraft"

sound_style_var.set(selected_style)

sound_enabled = True
music_enabled = True


def extract_translation_variables(translations):
    """
    Extract and set translation variables as global variables.

    Args:
        translations (dict): A dictionary containing translation key-value pairs.

    Returns:
        None
    """
    for key, value in translations.items():
        globals()[key] = value


def load_translations(language_file):
    """
     Load translations from a language file and return them as a dictionary.

     Args:
         language_file (str): The path to the language file.

     Returns:
         dict: A dictionary containing translation key-value pairs.
     """
    try:
        with open(f'materials/languages/{language_file}', 'r', encoding='utf-8') as json_file:
            translations = json.load(json_file)
            return translations
    except FileNotFoundError:
        return {}  # Return an empty dictionary if the language file doesn't exist


def play_sound(sound, is_music):
    global sound_enabled, sound_style_var

    if sound_enabled and is_music == 0:
        sound.play()

    if music_enabled and is_music:
        sound.play()


def open_help():
    """
     the open_help function creates a separate window that displays game rules
     and license information, with customized styling for the text, and centers
     the window on the screen for user convenience
    """
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
    # uses in open_settings()
    global selected_language

    if language in language_files:
        selected_language = language
        language_file = language_files[language]
        translations = load_translations(language_file)
        extract_translation_variables(translations)
    else:
        print(f"Language '{language}' is not supported.")


update_language(selected_language)


def save_settings():
    # saves settings in open_settings()
    global sound_enabled, music_enabled
    music_enabled = music_enabled_var.get()
    sound_enabled = sound_enabled_var.get()
    sound_style = sound_style_var.get()
    selected_language = language_var.get()
    # Update the language based on the user's choice
    update_language(selected_language)
    update_ui_language()
    settings_window.destroy()


def open_settings():
    """
    the open_settings function creates a settings window with options for
    configuring music, sound, sound style, and language settings. Users can
    enable or disable music and sound, select a sound style, and choose a language.
     The selected settings can be saved using the "Save" button.
    """
    global sound_enabled, music_enabled, sound_style_var, language_var, selected_language, settings_window, \
        music_enabled_var, sound_enabled_var, selected_style

    settings_window = Toplevel()
    settings_window.title(menu_settings)
    settings_window.geometry("390x180")

    music_enabled_var = IntVar(value=music_enabled)
    music_checkbox = Checkbutton(settings_window, text=menu_settings_music_checkbox, variable=music_enabled_var,
                                 font=("Arial", 12))
    music_checkbox.grid(row=0, column=0, padx=20)

    sound_enabled_var = IntVar(value=sound_enabled)
    sound_checkbox = Checkbutton(settings_window, text=menu_settings_sound_checkbox, variable=sound_enabled_var,
                                 font=("Arial", 12))
    sound_checkbox.grid(row=1, column=0, padx=20)

    sound_style_label = Label(settings_window, text=menu_settings_sound_style, font=("Arial", 12))
    sound_style_label.grid(row=2, column=0, padx=10, pady=5)

    sound_style_combobox = ttk.Combobox(settings_window, textvariable=sound_style_var,
                                        values=["maincraft", "girly", "cow"], font=("Arial", 12))
    sound_style_combobox.grid(row=2, column=1)

    language_label = Label(settings_window, text=menu_settings_language, font=("Arial", 12))
    language_label.grid(row=3, column=0, padx=10, pady=5)

    language_var = StringVar()
    language_combobox = ttk.Combobox(
        settings_window, textvariable=language_var, values=list(language_files.keys()), font=("Arial", 12)
    )
    language_combobox.grid(row=3, column=1)

    language_var.set(selected_language)

    save_button = Button(settings_window, text=menu_settings_save, command=save_settings, font=("Arial", 12))
    save_button.grid(row=4, columnspan=2, pady=10)


def update_ui_language():
    """
    the update_ui_language function is used to update various UI elements,
    such as labels, buttons, menu items, and error messages, to reflect changes
    in the selected language. It ensures that the game's UI is presented in a way
    that is easily understandable to the player in their chosen language
    """
    global main_menu, username_label, is_on_win_screen, canvas_text_score, elapsed_time_formatted, restart_button
    username_label.config(text=f"{prompt_username}: {current_username}")


    restart_button.config(text=restart_button_text)
    pause_button.config(text=pause_button_text)
    main_menu.entryconfig(1, label=menu_records, command=open_records)
    main_menu.entryconfig(2, label=menu_settings, command=open_settings)
    main_menu.entryconfig(3, label=menu_help, command=open_help)
    main_menu.entryconfig(4, label=menu_exit, command=exit_app)
    errmsg.set(message_enter_between)
    if is_on_win_screen:
        canvas_text_score.delete("all")  # This will delete all items on the canvas
        canvas_text_score.create_text(
            160, 40,  # Center the text
            text=f"{message_you_win}\n{message_your_score} {label_time} - {elapsed_time_formatted}, Bulls - {num_losses}",
            font=("Arial", 13),
            fill="black"
        )
        if pygame.mixer.get_busy():
            play_sound(win_sound, 1)


def exit_app():
    root.quit()


def get_last_username():
    """
    needs for printing the username of the last player

      Args: None

     Returns:
         part.replace("Username: ", "") or "Cool Name" - username
    """
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


def create_main_screen():
    """
    Create the main game screen with input fields, buttons, and labels.

    This function initializes and displays the main game screen, including input fields for the player's guesses,
    buttons to control the game (restart and pause/resume), image canvases for displaying feedback images (bulls and cows),
    and labels to show game statistics and the timer.

    Args:
        None

    Returns:
        None
    """
    global entry_vars, entry_fields, main_screen_objects, canvas_bull,\
        image_bull, canvas_cow, image_cow, error_label, win_sound, is_game_paused,\
        paused_time, start_time, pause_button, timer_label, start_game_time, current_username,\
        username_var, restart_button, pause_button_text, username_label, restart_button_text

    # Define fonts for text elements
    font1 = font.Font(family="Arial", size=20, weight="normal", slant="roman")
    font_label = font.Font(family="Arial", size=14, weight="normal", slant="roman")
    font_label_10 = font.Font(family="Arial", size=10, weight="normal", slant="roman")

    # Initialize lists to hold entry variables, entry fields, and other screen objects
    entry_vars = []
    entry_fields = []
    main_screen_objects = []

    # Initialize game timer variables
    timer_id = None
    start_time = time.time()
    start_game_time = datetime.now()
    current_username = get_last_username()

    # Create and place input fields for guesses
    for i in range(4):
        var = StringVar()
        entry_var = ttk.Entry(
            textvariable=var,
            validate="key",
            validatecommand=(root.register(is_valid), "%P", i),
            font=font1,
            width=3
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

    # Create and place the username label and entry field
    username_label = Label(
        root,
        foreground="black",
        text=f"{prompt_username}: {current_username}",
        font=font_label_10,
        background="white",
        borderwidth=2,
        relief="ridge"
    )
    username_label.place(x=100, y=0)
    username_label.bind("<Button-1>", switch_to_entry)

    username_entry = Entry(root, font=font_label_10, width=15)
    username_entry.bind('<Return>', update_username)
    username_entry.bind("<FocusOut>", update_username)

    # Create and place the restart button
    restart_button = Button(
        text=restart_button_text,
        command=restart_game,
        background="lightskyblue"
    )
    restart_button.place(x=SCREEN_WIDTH / 2, y=SCREEN_HEIGHT - 40)

    def toggle_pause():
        """
        allows the player to pause and resume the game, updating the UI
        and managing the game's pause state, including the timer and entry field states.
        """
        global is_game_paused, start_time, paused_time, pause_button, pause_button_text, resume_button
        if is_game_paused:
            # Resume the game timer
            is_game_paused = False
            pause_button.config(text=pause_button_text)
            start_time = time.time() - paused_time

            for i in range(4):
                entry_value = entry_fields[i].get()
                if entry_value.isdigit():
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

    # Create and place the pause button
    pause_button = Button(
        text=pause_button_text,
        command=toggle_pause,
        background="lightcoral"
    )
    pause_button.place(x=SCREEN_WIDTH / 2 - 70, y=SCREEN_HEIGHT - 40)
    main_screen_objects.append(pause_button)

    # Create and place image canvases for bulls and cows feedback
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

    # Create and place labels for game statistics and the timer
    winsmsg.set("Cows: 0")
    lossesmsg.set("Bulls: 0")

    error_label = ttk.Label(
        foreground="red",
        textvariable=errmsg,
        font=font_label,
        background="white"
    )
    error_label.place(x=60, y=300)
    main_screen_objects.append(error_label)

    num_wins_label = ttk.Label(
        foreground="black",
        textvariable=winsmsg,
        font=font_label,
        background="white"
    )
    num_wins_label.place(x=60, y=50)
    main_screen_objects.append(num_wins_label)

    num_losses_label = ttk.Label(
        foreground="black",
        textvariable=lossesmsg,
        font=font_label,
        background="white"
    )
    num_losses_label.place(x=60, y=150)
    main_screen_objects.append(num_losses_label)

    # Create and place a label to display the game timer
    timer_label = ttk.Label(
        foreground="black",
        text="Time: 0:00",
        font=font_label_10,
        background="white",
        borderwidth=2,
        relief="ridge"
    )
    timer_label.place(x=331, y=0)
    main_screen_objects.append(timer_label)

    # Update the game timer
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
    """
     Restart the game by resetting game variables, generating new random values, and clearing input fields.

     This function is called when the player decides to restart the game. It stops any playing win sound,
     resets the game statistics (number of wins and losses), restarts the timer, generates new random values,
     clears the input fields, resets the labels, and hides the win screen if it was displayed.
     """
    global num_wins, num_losses, random_values, start_time, paused_time, is_game_paused,\
        win_sound, start_game_time, username_label, restart_button

    win_sound.stop()

    num_wins = 0
    num_losses = 0
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
        hide_win_screen()
        username_label.destroy()
        create_main_screen()
    if is_game_paused:
        is_game_paused = False
        pause_button.config(text=pause_button_text)
        # Update the timer label to display "Time: 0:00"
    timer_label.config(text="Time: 0:00")
    # Update the timer immediately
    update_timer()

def hide_win_screen():
    canvas_win.place_forget()
    canvas_text_score.place_forget()
    is_on_win_screen = False


def enlarge_bull():
    update_image(canvas_bull, 2, "materials/Optimized-bull2.PNG")
    root.after(1000, reset_bull_scale)  # Schedule the reset after 1 second


def enlarge_cow():
    canvas_cow.place(in_=root, x=150, y=30)
    update_image(canvas_cow, 2, "materials/Optimized-cow.PNG")
    root.after(1000, reset_cow_scale)  # Schedule the reset after 1 second


def reset_bull_scale():
    update_image(canvas_bull, 1, "materials/Optimized-bull2.PNG")


def reset_cow_scale():
    update_image(canvas_cow, 1, "materials/Optimized-cow.PNG")


def update_image(canvas, scale, path):
    canvas.config(width=PHOTO_SCALE * scale, height=PHOTO_SCALE * scale)
    image = Image.open(path).resize((PHOTO_SCALE * scale, PHOTO_SCALE * scale))
    image = ImageTk.PhotoImage(image)
    canvas.create_image(0, 0, image=image, anchor=NW)
    canvas.image = image  # Keep a reference to the image to prevent it from being garbage collected


def display_image_sequence(window, image_folder):
    """
    Display a sequence of images in a tkinter window.

    Args:
        window (tkinter.Tk or tkinter.Canvas): The window or canvas to display the images.
        image_folder (str): The folder containing image files.

    This function continuously updates the displayed image in the given window or canvas by cycling through
    the images found in the specified folder.

    Example usage:
    display_image_sequence(window, "path/to/image_folder")
    """
    image_files = sorted([
        os.path.join(image_folder, filename)
        for filename in os.listdir(image_folder)
        if filename.endswith(".png")
    ])
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
    """
    Validate the user's input in a number-guessing game.

    This function checks if the user's input is valid, updates game statistics, and plays sounds accordingly.

    Args:
        new_val (str): The user's input.
        entry_idx (int): The index of the input field.

    Returns:
        bool: True if the input is valid, otherwise False.
    """
    try:
        global num_wins, num_losses, happy_girl_sound, classic_sound, girly_sound, style_3_sound, sound_style_var, \
            sad_girl_sound, happy_cow_sound, error_maincraft_sound, happy_maincraft_sound, angry_cow_sound

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

                # Play sound based on the selected style
                if sound_style_var.get() == "maincraft":
                    play_sound(happy_maincraft_sound, 0)
                elif sound_style_var.get() == "girly":
                    play_sound(happy_girl_sound, 0)
                elif sound_style_var.get() == "cow":
                    play_sound(happy_cow_sound, 0)

                if num_wins == 4:
                    show_win_screen()
            else:
                num_losses += 1
                error_label.config(foreground="red")
                errmsg.set(message_not_a_match)
                lossesmsg.set("Bulls: " + str(num_losses))
                enlarge_bull()

                if sound_style_var.get() == "maincraft":
                    play_sound(error_maincraft_sound, 0)
                elif sound_style_var.get() == "girly":
                    play_sound(sad_girl_sound, 0)
                elif sound_style_var.get() == "cow":
                    play_sound(angry_cow_sound, 0)

        elif len(new_val) != 1:
            error_label.config(foreground="red")
            errmsg.set(message_enter_single_digit)
            lossesmsg.set("Bulls: " + str(num_losses))
        else:
            error_label.config(foreground="red")
            errmsg.set(message_enter_between)

    except ValueError:
        error_label.config(foreground="red")
        errmsg.set(message_enter_valid_integer)

    return True


def show_win_screen():
    """
    Display the win screen when the player wins the game.

    This function calculates the elapsed time, stores the game results in the "records.txt" file,
    and displays the win screen with the player's score.

    Args:
        None

    Returns:
        None
    """
    global restart_button, canvas_win, is_on_win_screen, canvas_text_score, win_sound, \
        start_game_time, current_username, elapsed_time, elapsed_time_formatted

    end_time = datetime.now()  # Store the game end time
    elapsed_time = end_time - start_game_time  # Calculate the elapsed time
    formatted_end_time = end_time.strftime("%d.%m.%Y")  # Format the end time as "dd.mm.yyyy"

    elapsed_time_seconds = elapsed_time.total_seconds()
    elapsed_time_formatted = str(datetime.utcfromtimestamp(elapsed_time_seconds).strftime('%M:%S'))

    # Write game results (number of bulls, time, and date) to the "records.txt" file
    with open("records.txt", "a") as records_file:
        records_file.write(
            f"Username: {current_username}, Bulls: {num_losses}, Time: {elapsed_time}, Date: {formatted_end_time}\n")

    is_on_win_screen = True

    play_sound(win_sound, 1)

    # Hide the entries and labels
    for object_main_screen in main_screen_objects:
        object_main_screen.grid_forget()
        object_main_screen.place_forget()

    canvas_win = Canvas(bg="white", width=SCREEN_WIDTH, height=SCREEN_HEIGHT, highlightthickness=0,
                        relief='ridge')
    canvas_win.place(x=0, y=0)
    display_image_sequence(canvas_win, "materials/cow-gif")
    restart_button.destroy()

    restart_button = Button(canvas_win, text=restart_button_text, command=restart_game, background="lightskyblue")
    canvas_win.create_window(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 40, window=restart_button)

    canvas_text_score = Canvas(bg="gray97", width=SCREEN_WIDTH - 30, height=SCREEN_HEIGHT / 4 - 50,
                               highlightthickness=0, relief='ridge')
    canvas_text_score.create_text(
        160, 40,  # Center the text
        text=f"{message_you_win}\n{message_your_score} {label_time} - {elapsed_time_formatted}, Bulls - {num_losses}",
        font=("Arial", 13),
        fill="black"
    )
    canvas_text_score.place(x=20, y=20)


random_values = [randint(0, 9) for _ in range(4)]
print(random_values)

# Create a themed menu
main_menu = Menu(root)
root.config(menu=main_menu)

# SOUNDS -----------------------------------------------------------

win_sound = pygame.mixer.Sound("materials/audio/win.mp3")
happy_girl_sound = pygame.mixer.Sound("materials/audio/happy-girl.mp3")
sad_girl_sound = pygame.mixer.Sound("materials/audio/angry-girl.mp3")
happy_cow_sound = pygame.mixer.Sound("materials/audio/cow.mp3")
angry_cow_sound = pygame.mixer.Sound("materials/audio/angry-cow.mp3")
error_maincraft_sound = pygame.mixer.Sound("materials/audio/inecraft_death.mp3")
happy_maincraft_sound = pygame.mixer.Sound("materials/audio/inecraft_levelu.mp3")

main_menu.add_command(label=menu_records, command=open_records)
main_menu.add_command(label=menu_settings, command=open_settings)
main_menu.add_command(label=menu_help, command=open_help)
main_menu.add_command(label=menu_exit, command=exit_app)

create_main_screen()

root.config(menu=main_menu)
root.mainloop()
