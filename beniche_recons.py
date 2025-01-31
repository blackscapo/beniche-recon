import tkinter as tk
from tkinter import messagebox, filedialog
from tkinter import ttk
import threading
import os
import pyfiglet  # Importing pyfiglet for ASCII art generation

# Global variable to store the paths of the selected database files
selected_file_paths = []

# Function to open the folder dialog and scan all .txt files
def select_folder():
    global selected_file_paths
    folder_path = filedialog.askdirectory(title="Select Folder Containing .txt Files")
    
    if folder_path:
        # Scan for .txt files in the selected folder (and optionally subfolders)
        selected_file_paths = []
        for root, _, files in os.walk(folder_path):
            for file in files:
                if file.endswith(".txt"):
                    selected_file_paths.append(os.path.join(root, file))
        
        # Update the label showing number of files found
        file_paths_label.config(text=f"Found {len(selected_file_paths)} .txt files in folder")
    else:
        file_paths_label.config(text="Selected Files: None")

# Function to read data from a selected file (single file)
def read_from_file(file_path):
    try:
        with open(file_path, "r") as file:
            return file.readlines()  # Return lines as a list
    except Exception as e:
        messagebox.showerror("Error", f"Failed to read {file_path}: {str(e)}")
        return []

# Function to update the list box with search results
def on_search():
    query = search_entry.get()  # Get the query from the search box
    if not query:
        messagebox.showwarning("Input Error", "Please enter a search term.")
        return
    
    if not selected_file_paths:
        messagebox.showwarning("Input Error", "No folder selected or no .txt files found.")
        return
    
    # Start the progress bar
    progress_bar["value"] = 0
    search_button.config(state=tk.DISABLED)  # Disable the search button during the search

    # Run the search function in a separate thread so it doesn't block the UI
    threading.Thread(target=search_thread, args=(query,)).start()

# Function to perform the search on each file one by one
def search_thread(query):
    # Clear the list box before adding new results
    result_listbox.delete(0, tk.END)
    total_files = len(selected_file_paths)
    
    # Iterate through the files one by one
    for index, file_path in enumerate(selected_file_paths):
        # Display which file is being searched in the list box
        result_listbox.insert(tk.END, f"🔍 Searching in: {file_path}")
        result_listbox.yview(tk.END)  # Scroll to the latest inserted line
        
        # Read the data from the current file
        lines = read_from_file(file_path)
        
        # Filter the results based on the query (email or password search)
        filtered_results = [line.strip() for line in lines if query.lower() in line.lower()]
        
        if filtered_results:
            # If results are found, add them to the list box
            for result in filtered_results:
                result_listbox.insert(tk.END, f"  ➡️ {result}")  # Indent the results for readability
        else:
            # If no results found for this file, indicate that
            result_listbox.insert(tk.END, "  ✖️ No results found for this file.")
        
        result_listbox.insert(tk.END, "")  # Add a blank line between file results for readability
        
        # Update progress bar
        progress_bar["value"] = (index + 1) / total_files * 100
        root.update_idletasks()
    
    # Reset progress bar and re-enable the search button
    progress_bar["value"] = 0
    search_button.config(state=tk.NORMAL)
    messagebox.showinfo("Search Complete", "Search finished!")

# Function to clear search results and input
def clear_results():
    result_listbox.delete(0, tk.END)
    search_entry.delete(0, tk.END)
    result_count_label.config(text="Results Found: 0")

# Function to export search results to a file
def export_results():
    if not result_listbox.get(0, tk.END):
        messagebox.showwarning("Export Error", "No results to export.")
        return
    
    export_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
    if export_path:
        with open(export_path, "w") as file:
            for line in result_listbox.get(0, tk.END):
                file.write(line + "\n")
        messagebox.showinfo("Export Successful", f"Results exported to {export_path}")

# Set up the main window (root window)
root = tk.Tk()
root.title("Beniche-recons")
root.geometry("400x600")  # Resize the app to be more compact
root.config(bg="#2c3e50")  # Dark theme background

# Add some padding around the window for a more spacious layout
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)

# Generate ASCII art for "Beniche-recons" using pyfiglet
ascii_art = pyfiglet.figlet_format("Beniche-recons", font="slant")  # You can change the font here if you like

# Create a label to display the ASCII art as the header
header_label = tk.Label(root, text=ascii_art, fg="#1abc9c", bg="#2c3e50", font=("Courier New", 8), anchor="w")
header_label.grid(row=0, pady=10)

# Create a label for the search box
search_label = tk.Label(root, text="Enter search query:", fg="#1abc9c", bg="#2c3e50", font=("Segoe UI", 12))
search_label.grid(row=1, pady=10)

# Create an entry widget for the search box
search_entry = tk.Entry(root, width=40, fg="white", bg="#34495e", font=("Segoe UI", 12), borderwidth=2, relief="solid")
search_entry.grid(row=2, pady=10)

# Create a search button
search_button = tk.Button(root, text="Search", command=on_search, fg="white", bg="#1abc9c", font=("Segoe UI", 12, "bold"), relief="raised", bd=4, width=15)
search_button.grid(row=3, pady=10)

# Create a label for showing the number of results found
result_count_label = tk.Label(root, text="Results Found: 0", fg="#1abc9c", bg="#2c3e50", font=("Segoe UI", 10))
result_count_label.grid(row=4, pady=10)

# Create a button for selecting a folder
select_folder_button = tk.Button(root, text="Select Folder", command=select_folder, fg="white", bg="#1abc9c", font=("Segoe UI", 12, "bold"), relief="raised", bd=4)
select_folder_button.grid(row=5, pady=10)

# Label to display the selected folder and file count
file_paths_label = tk.Label(root, text="Selected Folder: None", fg="#1abc9c", bg="#2c3e50", font=("Segoe UI", 10))
file_paths_label.grid(row=6, pady=10)

# Create a frame for the listbox and scrollbar (make it occupy 80% of the height)
listbox_frame = tk.Frame(root, bg="#2c3e50")
listbox_frame.grid(row=7, pady=10, padx=10, sticky="nsew")

# Create a listbox to display the results
result_listbox = tk.Listbox(listbox_frame, width=50, height=15, fg="white", bg="#34495e", font=("Courier New", 12), selectmode=tk.SINGLE, bd=3, relief="solid")
result_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Add a scrollbar to the listbox
scrollbar = tk.Scrollbar(listbox_frame, orient="vertical", command=result_listbox.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
result_listbox.config(yscrollcommand=scrollbar.set)

# Create a progress bar to show the search status
progress_bar = ttk.Progressbar(root, orient="horizontal", length=370, mode="determinate")
progress_bar.grid(row=8, pady=10)

# Create a "Clear Results" button
clear_button = tk.Button(root, text="Clear Results", command=clear_results, fg="white", bg="#e74c3c", font=("Segoe UI", 12, "bold"), relief="raised", bd=4)
clear_button.grid(row=9, pady=10)

# Create an "Export Results" button
export_button = tk.Button(root, text="Export Results", command=export_results, fg="white", bg="#3498db", font=("Segoe UI", 12, "bold"), relief="raised", bd=4)
export_button.grid(row=10, pady=10)

# Run the main event loop
root.mainloop()
