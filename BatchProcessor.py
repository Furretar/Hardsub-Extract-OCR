import os
import tkinter as tk
from tkinter import filedialog, messagebox
from google.cloud import vision
import threading

def parse_filename(filename):
    try:
        base_name = filename.rsplit('.', 1)[0]
        timestamps = base_name.split("__")
        if len(timestamps) != 2:
            raise ValueError(f"Invalid filename format: {filename}")
        start_ts = timestamps[0]
        end_ts_parts = timestamps[1].split("_")[:4]
        if len(end_ts_parts) != 4:
            raise ValueError(f"Invalid end timestamp format in {filename}")
        end_ts = "_".join(end_ts_parts)
        return start_ts, end_ts
    except Exception as e:
        raise ValueError(f"Error parsing filename {filename}: {e}")

def format_timestamp(timestamp):
    try:
        parts = timestamp.split("_")
        if len(parts) != 4:
            raise ValueError(f"Invalid timestamp format: {timestamp}")
        hours, minutes, seconds, milliseconds = map(int, parts)
        return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"
    except Exception as e:
        raise ValueError(f"Error formatting timestamp {timestamp}: {e}")

def get_unique_filename(file_path):
    base, ext = os.path.splitext(file_path)
    counter = 1
    while os.path.exists(file_path):
        file_path = f"{base}_{counter}{ext}"
        counter += 1
    return file_path

def generate_srt_for_folder(image_folder, output_srt, client, logs, update_log_callback=None):
    srt_lines = []
    counter = 1
    output_srt = get_unique_filename(output_srt)
    for file in sorted(os.listdir(image_folder)):
        if file.endswith((".png", ".jpeg")):
            try:
                start_ts, end_ts = parse_filename(file)
                start_time = format_timestamp(start_ts)
                end_time = format_timestamp(end_ts)
                image_path = os.path.join(image_folder, file)
                with open(image_path, "rb") as img_file:
                    content = img_file.read()
                image = vision.Image(content=content)
                response = client.text_detection(image=image)
                if response.text_annotations:
                    extracted_text = response.text_annotations[0].description.strip()
                    log = f"Processing {file}...\nText: {extracted_text}\n"
                    logs.append(log)
                    srt_lines.append(f"{counter}\n{start_time} --> {end_time}\n{extracted_text}\n\n")
                    counter += 1
                else:
                    logs.append(f"No text detected in {file}\n")
                if update_log_callback:
                    update_log_callback(logs[-1])
            except ValueError as ve:
                logs.append(f"Skipping file {file}: {ve}")
                if update_log_callback:
                    update_log_callback(logs[-1])
    if srt_lines:
        with open(output_srt, "w", encoding="utf-8") as srt_file:
            srt_file.writelines(srt_lines)
        logs.append(f"SRT file saved to {output_srt}\n")
        if update_log_callback:
            update_log_callback(logs[-1])
    else:
        logs.append(f"No valid files processed in {image_folder}\n")
        if update_log_callback:
            update_log_callback(logs[-1])

def process_images(image_dir, output_folder, json_path, recursive, update_log_callback=None):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = json_path
    client = vision.ImageAnnotatorClient()
    logs = []
    if recursive:
        txtimages_folders = [
            os.path.join(root, subdir)
            for root, dirs, _ in os.walk(image_dir)
            for subdir in dirs
            if subdir == "TXTImages"
        ]
        if not txtimages_folders:
            logs.append(f"No TXTImages folder found in {image_dir}\n")
            if update_log_callback:
                update_log_callback(logs[-1])
        else:
            for txt_folder in txtimages_folders:
                output_srt = os.path.join(output_folder, f"{os.path.basename(os.path.dirname(txt_folder))}_output.srt")
                generate_srt_for_folder(txt_folder, output_srt, client, logs, update_log_callback)
    else:
        output_srt = os.path.join(output_folder, "output.srt")
        generate_srt_for_folder(image_dir, output_srt, client, logs, update_log_callback)
    return logs

def select_folder(entry, title="Select Folder"):
    folder = filedialog.askdirectory(title=title)
    if folder:
        entry.delete(0, tk.END)
        entry.insert(0, folder)

def select_json(entry):
    file = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
    if file:
        entry.delete(0, tk.END)
        entry.insert(0, file)

def select_output_folder(entry):
    folder = filedialog.askdirectory(title="Select Output Folder")
    if folder:
        entry.delete(0, tk.END)
        entry.insert(0, folder)

def run_program(folder_entry, output_folder_entry, json_entry, recursive_var, log_text):
    image_dir = folder_entry.get()
    output_folder = output_folder_entry.get()
    json_path = json_entry.get()
    recursive = recursive_var.get()

    if not os.path.isdir(image_dir):
        messagebox.showerror("Error", "Please select a valid folder with images.")
        return
    if not json_path.endswith(".json") or not os.path.isfile(json_path):
        messagebox.showerror("Error", "Please select a valid JSON credentials file.")
        return
    if not os.path.isdir(output_folder):
        messagebox.showerror("Error", "Please select a valid output folder.")
        return

    run_button.config(state=tk.DISABLED)
    log_text.delete(1.0, tk.END)
    log_text.insert(tk.END, "Processing started...\n")

    def process_thread():
        try:
            def update_log(new_log):
                log_text.insert(tk.END, new_log)
                log_text.yview(tk.END)

            logs = process_images(image_dir, output_folder, json_path, recursive, update_log)
            log_text.insert(tk.END, "Processing completed.\n")
            log_text.yview(tk.END)
        except Exception as e:
            log_text.insert(tk.END, f"An error occurred: {e}\n")
        finally:
            run_button.config(state=tk.NORMAL)

    threading.Thread(target=process_thread, daemon=True).start()

def main():
    root = tk.Tk()
    root.title("Image to SRT Converter")
    root.geometry("700x500")

    tk.Label(root, text="Folder with Images:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
    folder_entry = tk.Entry(root, width=50)
    folder_entry.grid(row=0, column=1, padx=10, pady=10)
    tk.Button(root, text="Browse", command=lambda: select_folder(folder_entry)).grid(row=0, column=2, padx=10, pady=10)

    tk.Label(root, text="Output Folder:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
    output_folder_entry = tk.Entry(root, width=50)
    output_folder_entry.grid(row=1, column=1, padx=10, pady=10)
    tk.Button(root, text="Browse", command=lambda: select_output_folder(output_folder_entry)).grid(row=1, column=2, padx=10, pady=10)

    tk.Label(root, text="JSON Credentials File:").grid(row=2, column=0, padx=10, pady=10, sticky="w")
    json_entry = tk.Entry(root, width=50)
    json_entry.grid(row=2, column=1, padx=10, pady=10)
    tk.Button(root, text="Browse", command=lambda: select_json(json_entry)).grid(row=2, column=2, padx=10, pady=10)

    recursive_var = tk.BooleanVar(value=False)
    tk.Checkbutton(root, text="Process Multiple Folders (Folder Containing Folders Containing TXTImages)", variable=recursive_var).grid(row=3, column=1, padx=10, pady=10, sticky="w")

    global run_button
    run_button = tk.Button(root, text="Convert", command=lambda: run_program(folder_entry, output_folder_entry, json_entry, recursive_var, log_text), bg="green", fg="white")
    run_button.grid(row=4, column=1, pady=20)

    log_text = tk.Text(root, width=80, height=15)
    log_text.grid(row=5, column=0, columnspan=3, padx=10, pady=10)

    root.mainloop()

if __name__ == "__main__":
    main()
