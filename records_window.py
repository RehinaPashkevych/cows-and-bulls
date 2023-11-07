import tkinter as tk
from tkinter import ttk
import re


def display_records_window():
    """
    This code provides a user-friendly way to display game records, including the best record,
    in a separate window with customizable column widths and alternating row colors for improved readability.
    """
    def resize_columns(event):
        # Get the current window width
        window_width = event.width

        # Resize the columns proportionally based on the window width
        column_width = window_width // 4  # Divide the width into 4 columns
        records_tree.column("Username", width=column_width)
        records_tree.column("Bulls", width=column_width)
        records_tree.column("Time", width=column_width)
        records_tree.column("Date", width=column_width)

    records_window = tk.Toplevel()
    records_window.title("Records")

    # Create and configure a Treeview widget to display the records
    records_tree = ttk.Treeview(records_window, columns=("Username", "Bulls", "Time", "Date"), show="headings")
    records_tree.heading("Username", text="Username")
    records_tree.heading("Bulls", text="Bulls")
    records_tree.heading("Time", text="Time")
    records_tree.heading("Date", text="Date")
    records_tree.pack(fill=tk.BOTH, expand=True)

    # Bind the resize_columns function to the <Configure> event of the window
    records_window.bind("<Configure>", resize_columns)

    # Create a custom style for the Treeview
    style = ttk.Style()
    style.configure("Treeview.Treeview", background="white", foreground="black")
    style.map("Treeview.Treeview", background=[("selected", "blue")])

    # Create a frame for the best result
    best_frame = tk.Frame(records_window, bg="yellow")
    best_frame.pack(fill=tk.X, padx=10, pady=5)

    best_result = None  # To keep track of the best result

    # Read records from a file and insert them into the Treeview
    try:
        with open("records.txt", "r") as records_file:
            records_data = records_file.read()
            records = [line.split(", ") for line in records_data.strip().split('\n')]

            for i, record in enumerate(records):
                if len(record) >= 4:  # Make sure there are at least 4 elements in the record
                    username = record[0].split(": ")[1]
                    bulls_match = re.search(r'Bulls: (\d+)', record[1])
                    time_match = re.search(r'Time: (\d+:\d+:\d+(?:\.\d+)?)', record[2])
                    date_match = re.search(r'Date: (\d+\.\d+\.\d+)', record[3]) if len(
                        record) > 3 else None  # Extract the date

                    if username and bulls_match and time_match:
                        bulls = bulls_match.group(1)
                        time_str = time_match.group(1)
                        date_str = date_match.group(1) if date_match else ""  # Check if date_match is not None

                        if i % 2 == 0:
                            records_tree.insert("", "end", values=(username, int(bulls), time_str, date_str),
                                                tags=("even_row",))
                        else:
                            records_tree.insert("", "end", values=(username, int(bulls), time_str, date_str),
                                                tags=("odd_row",))

                        if best_result is None or (int(bulls) <= best_result[1] and (time_str < best_result[2])):
                            best_result = (username, int(bulls), time_str, date_str)

            if best_result:
                # Display the best record in the best frame
                best_text = f"Best Result: Username: {best_result[0]}, Bulls: {best_result[1]}, Time: {best_result[2]}, Date: {best_result[3]}"
                best_result_label = tk.Label(best_frame, text=best_text, font=("Courier New", 12), bg="yellow")
                best_result_label.pack()

            records_tree.tag_configure("even_row", background="lightblue")
            records_tree.tag_configure("odd_row", background="lightyellow")

    except FileNotFoundError:
        # Handle the case where no records are found
        records_tree.insert("", "end", values=("No records found", "", "", ""))


if __name__ == "__main__":
    display_records_window()
