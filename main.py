import os
import time
from random import randint
from tkinter import *
from tkinter import ttk, font
from PIL import Image, ImageTk
import pygame  # Import pygame
from tkdnd import TkinterDnD

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
win_sound = None

is_on_win_screen = False
is_game_paused = False

errmsg = StringVar()
winsmsg = StringVar()
lossesmsg = StringVar()

paused_time = 0


def open_records():
    pass  # Add your action here


def open_settings():
    pass  # Add your action here


def open_help():
    pass  # Add your action here


def exit_app():
    root.quit()


def create_main_screen():
    global entry_vars, entry_fields, main_screen_objects, canvas_bull, \
        image_bull, canvas_cow, image_cow, error_label, win_sound, \
        happy_girl_sound, is_game_paused, paused_time, start_time, pause_button, timer_label

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

    # BUTTONS --------------------------------------------------------

    restart_button = Button(text="Restart", command=restart_game, background="lightskyblue")
    restart_button.place(x=SCREEN_WIDTH / 2, y=SCREEN_HEIGHT - 40)

    def toggle_pause():
        global is_game_paused, start_time, paused_time, pause_button
        if is_game_paused:
            # Resume the game timer
            is_game_paused = False
            pause_button.config(text="Pause")
            start_time = time.time() - paused_time
            for entry_field in entry_fields:
                entry_field.config(state="normal")
            # Update the timer immediately
            update_timer()
        else:
            pause_button.config(text="Resume")
            is_game_paused = True
            paused_time = time.time() - start_time
            for entry_field in entry_fields:
                entry_field.config(state="readonly")
            if timer_id is not None:
                root.after_cancel(timer_id)

    pause_button = Button(text="Pause", command=toggle_pause, background="lightcoral")
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
        timer_label.config(text=f"Time: {minutes}:{seconds:02}")
        # Continue updating the timer
        timer_id = root.after(1000, update_timer)

def restart_game():
    global num_wins, num_losses, random_values, start_time, current_time, paused_time, is_game_paused, pause_button

    pygame.mixer.music.stop()  # Stop any currently playing music

    num_wins = 0
    num_losses = 0
    current_time = 0
    paused_time = 0
    start_time = time.time()
    random_values = [randint(0, 9) for _ in range(4)]

    # Clear the entry fields
    for entry_field in entry_fields:
        entry_field.delete(0, "end")
        entry_field.config(state="normal")

    # Reset labels
    winsmsg.set("Cows: 0")
    lossesmsg.set("Bulls: 0")
    errmsg.set("")


    if is_on_win_screen:
        create_main_screen()
    if is_game_paused:
        is_game_paused = False
        pause_button.config(text="Pause")
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


def show_win_screen():
    global restart_button, canvas_win, is_on_win_screen, canvas_text_score, win_sound
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

    restart_button = Button(canvas_win, text="Restart", command=restart_game, background="lightskyblue")
    canvas_win.create_window(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 40, window=restart_button)

    canvas_text_score = Canvas(bg="gray97", width=SCREEN_WIDTH - 30, height=SCREEN_HEIGHT / 4 - 50,
                               highlightthickness=0, relief='ridge')
    canvas_text_score.create_text(
        160, 40,  # Center the text
        text=f"You Win!\nYour Score: Cows: {num_wins}, Bulls: {num_losses}",
        font=("Arial", 16),
        fill="black"
    )
    canvas_text_score.place(x=20, y=20)


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
                errmsg.set("Correct guess!")
                num_wins += 1
                winsmsg.set("Cows: " + str(num_wins))
                enlarge_cow()
                happy_girl_sound.play()
                if num_wins == 4:
                    show_win_screen()
            else:
                num_losses += 1
                error_label.config(foreground="red")
                errmsg.set("Not a match, keep trying.")
                lossesmsg.set("Bulls: " + str(num_losses))
                enlarge_bull()
        elif len(new_val) != 1:
            # num_losses += 1
            error_label.config(foreground="red")
            errmsg.set("Please enter a single digit.")
            lossesmsg.set("Bulls: " + str(num_losses))
        else:
            # num_losses += 1
            error_label.config(foreground="red")
            errmsg.set("Please enter an integer between 0 and 9.")
            lossesmsg.set("Bulls: " + str(num_losses))
    except ValueError:
        error_label.config(foreground="red")
        errmsg.set("Please enter a valid integer.")
    return True


random_values = [randint(0, 9) for _ in range(4)]
print(random_values)

# Create a themed menu
main_menu = Menu(root)
root.config(menu=main_menu)

main_menu.add_command(label="Records", command=open_records)
main_menu.add_command(label="Settings", command=open_settings)
main_menu.add_command(label="Help", command=open_help)
main_menu.add_separator()
main_menu.add_command(label="Exit", command=exit_app)

create_main_screen()

root.config(menu=main_menu)
root.mainloop()
