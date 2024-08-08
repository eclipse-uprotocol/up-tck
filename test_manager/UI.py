import os
import subprocess
import threading
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, scrolledtext, ttk

from PIL import Image, ImageTk  # Import PIL for image handling
from tkinterweb import HtmlFrame


def list_feature_files(directory):
    feature_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".feature"):
                feature_files.append(os.path.relpath(os.path.join(root, file), directory))
    return feature_files


def run_tests():
    global proc
    fname = feature_files_var.get()
    language1 = language1_var.get()
    transport1 = transport1_var.get()
    language2 = language2_var.get()
    transport2 = transport2_var.get()

    if (
        not fname
        or language1 not in languages
        or transport1 not in transports
        or language2 not in languages_with_blank
        or transport2 not in transports
    ):
        messagebox.showerror("Invalid input", "Please select valid options for all fields.")
        return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"reports/{fname.replace('/', '_')}_{timestamp}.html"

    command = [
        "python3",
        "-m",
        "behave",
        "--define",
        f"uE1={language1}",
        "--define",
        f"uE2={language2}",
        "--define",
        f"transport1={transport1}",
        "--define",
        f"transport2={transport2}",
        "-i",
        fname,
        "--format",
        "html",
        "--outfile",
        report_file,
    ]

    print("Running command:", ' '.join(command))
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # Clear the output box
    output_textbox.delete('1.0', tk.END)

    for line in iter(proc.stdout.readline, ''):
        output_textbox.insert(tk.END, line)
        output_textbox.see(tk.END)
    for line in iter(proc.stderr.readline, ''):
        output_textbox.insert(tk.END, line)
        output_textbox.see(tk.END)

    proc.stdout.close()
    proc.stderr.close()
    proc.wait()

    inject_css(report_file)
    # Load the HTML report in the HTML viewer
    load_html_report(report_file)
    messagebox.showinfo("Success", "Test execution completed.")


def start_tests():
    test_thread = threading.Thread(target=run_tests)
    test_thread.start()


def stop_tests():
    global proc
    if proc:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            output_textbox.insert(tk.END, "Process forcefully terminated.\n")
            output_textbox.see(tk.END)
        else:
            output_textbox.insert(tk.END, "Process terminated gracefully.\n")
            output_textbox.see(tk.END)

        proc = None  # Reset the reference


def inject_css(report_file):
    css = """
    <style>
    body {
        font-family: Arial, sans-serif;
        margin: 0;
        padding: 20px;
        font-size: 25px;
        width: 100%;
        box-sizing: border-box;
    }
    h1, h2, h3 {
        color: #333;
    }
    table {
        width: 100%;
        border-collapse: collapse;
    }
    th, td {
        padding: 10px;
        text-align: left;
        border-bottom: 1px solid #ddd;
    }
    tr:nth-child(even) {
        background-color: #f9f9f9;
    }
    .passed {
        color: green;
    }
    .failed {
        color: red;
    }
    </style>
    """
    with open(report_file, 'r') as file:
        content = file.read()
    if '<style>' not in content:
        content = content.replace('</head>', css + '</head>')
    with open(report_file, 'w') as file:
        file.write(content)


def load_html_report(report_file):
    try:
        with open(report_file, 'r') as file:
            html_content = file.read()
        html_frame.load_html(html_content)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load HTML report: {e}")


def show_feature_file_content():
    fname = feature_files_var.get()
    if not fname:
        messagebox.showerror("Error", "No feature file selected.")
        return

    try:
        with open(os.path.join("features/tests", fname), 'r') as file:
            content = file.read()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to open feature file: {e}")
        return

    # Create a new window to display the file content
    content_window = tk.Toplevel(root)
    content_window.title("Feature File Content")

    # Add a text widget to the new window
    text_widget = tk.Text(content_window, wrap=tk.WORD, height=50, width=200)
    text_widget.pack(expand=True, fill=tk.BOTH)

    # Insert the content into the text widget
    text_widget.insert(tk.END, content)
    text_widget.config(state=tk.DISABLED)  # Make text widget read-only


# Initialize the GUI application
root = tk.Tk()
root.title("UP-TCK Test Runner")

# Load and display the image
image_path = "../screenshots/uprotocol_logo.png"
image = Image.open(image_path)
photo = ImageTk.PhotoImage(image)

# Create and place the image label at the top
image_label = tk.Label(root, image=photo)
image_label.grid(column=0, row=0, columnspan=2, padx=10, pady=5)

# Fetch feature files and set options
feature_files = list_feature_files("features/tests")
languages = ["python", "java", "rust", "cpp"]
transports = ["socket", "zenoh", "someip"]
languages_with_blank = languages + ["_blank_"]

# Define variables for selected options
feature_files_var = tk.StringVar()
language1_var = tk.StringVar()
transport1_var = tk.StringVar()
language2_var = tk.StringVar()
transport2_var = tk.StringVar()

# Set default values
feature_files_var.set(feature_files[0] if feature_files else "")
language1_var.set(languages[0])
transport1_var.set(transports[0])
language2_var.set(languages_with_blank[0])
transport2_var.set(transports[0])

style = ttk.Style()
style.configure("RunTests.TButton", background="lightgreen", foreground="black")
style.configure("StopTests.TButton", background="lightcoral", foreground="black")
style.configure("ShowFeatureFileContent.TButton", background="lightblue", foreground="black")

# Create and place the widgets
ttk.Label(root, text="Select Feature File:").grid(column=0, row=1, padx=10, pady=5, sticky=tk.W)
ttk.Combobox(root, textvariable=feature_files_var, values=feature_files, state="readonly", width=50).grid(
    column=1, row=1, padx=10, pady=5, sticky=tk.W
)

ttk.Label(root, text="Select Language1 Under Test:").grid(column=0, row=2, padx=10, pady=5, sticky=tk.W)
ttk.Combobox(root, textvariable=language1_var, values=languages, state="readonly", width=50).grid(
    column=1, row=2, padx=10, pady=5, sticky=tk.W
)

ttk.Label(root, text="Select Transport1 Under Test:").grid(column=0, row=3, padx=10, pady=5, sticky=tk.W)
ttk.Combobox(root, textvariable=transport1_var, values=transports, state="readonly", width=50).grid(
    column=1, row=3, padx=10, pady=5, sticky=tk.W
)

ttk.Label(root, text="Select Language2 Under Test:").grid(column=0, row=4, padx=10, pady=5, sticky=tk.W)
ttk.Combobox(root, textvariable=language2_var, values=languages_with_blank, state="readonly", width=50).grid(
    column=1, row=4, padx=10, pady=5, sticky=tk.W
)

ttk.Label(root, text="Select Transport2 Under Test:").grid(column=0, row=5, padx=10, pady=5, sticky=tk.W)
ttk.Combobox(root, textvariable=transport2_var, values=transports, state="readonly", width=50).grid(
    column=1, row=5, padx=10, pady=5, sticky=tk.W
)

# Apply the styles to the buttons
ttk.Button(root, text="Run Tests", command=start_tests, style="RunTests.TButton").grid(
    column=0, row=6, columnspan=1, padx=10, pady=20, sticky="w"
)
ttk.Button(root, text="Stop Tests", command=stop_tests, style="StopTests.TButton").grid(
    column=2, row=6, columnspan=1, padx=10, pady=20, sticky="w"
)
ttk.Button(
    root, text="Show Feature File Content", command=show_feature_file_content, style="ShowFeatureFileContent.TButton"
).grid(column=1, row=6, columnspan=1, padx=10, pady=5, sticky="w")

# Create a scrolled text widget to display terminal output
output_textbox = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=250, height=10)
output_textbox.grid(column=0, row=9, columnspan=2, padx=10, pady=5)

# Create an HTML frame widget to display the HTML report
html_frame = HtmlFrame(root, width=250, height=15)
html_frame.grid(column=0, row=8, columnspan=2, padx=10, pady=5, sticky="nsew")

# Configure grid row and column weights for resizing
root.grid_rowconfigure(8, weight=1)
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)

# Run the GUI event loop
root.mainloop()
