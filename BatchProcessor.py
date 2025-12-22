import os
import time
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
    candidate = file_path
    counter = 1
    while os.path.exists(candidate):
        candidate = f"{base}_{counter}{ext}"
        counter += 1
    return candidate

log_lock = threading.Lock()

def append_log(log_file, text, update_log_callback=None):
    with log_lock:
        try:
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(text if text.endswith("\n") else text + "\n")
        except Exception:
            pass
    if update_log_callback:
        try:
            update_log_callback(text if text.endswith("\n") else text + "\n")
        except Exception:
            pass

def generate_srt_for_folder(image_folder, output_srt, client, logs, log_file, update_log_callback=None):
    counter = 1
    output_srt = get_unique_filename(output_srt)
    appended_any = False
    supported_ext = (".png", ".jpeg", ".jpg", ".webp", ".bmp")
    for file in sorted(os.listdir(image_folder)):
        if not file.lower().endswith(supported_ext):
            continue
        try:
            start_ts, end_ts = parse_filename(file)
            start_time = format_timestamp(start_ts)
            end_time = format_timestamp(end_ts)
            image_path = os.path.join(image_folder, file)
            with open(image_path, "rb") as img_file:
                content = img_file.read()
            image = vision.Image(content=content)
            attempts = 0
            wait = 5
            while True:
                try:
                    response = client.text_detection(image=image)
                    break
                except Exception as e:
                    attempts += 1
                    err_msg = f"Connection error while processing {file}: {e} (attempt {attempts}), retrying in {wait}s"
                    logs.append(err_msg)
                    append_log(log_file, err_msg, update_log_callback)
                    time.sleep(wait)
                    wait = min(wait * 2, 60)
                    try:
                        client = vision.ImageAnnotatorClient()
                    except Exception:
                        pass
            if response.text_annotations:
                extracted_text = response.text_annotations[0].description.strip()
                entry = f"{counter}\n{start_time} --> {end_time}\n{extracted_text}\n\n"
                try:
                    with log_lock:
                        with open(output_srt, "a", encoding="utf-8") as srt_file:
                            srt_file.write(entry)
                    appended_any = True
                    log = f"Processed {file}: wrote subtitle #{counter}"
                    logs.append(log)
                    append_log(log_file, f"{log}\nText: {extracted_text}", update_log_callback)
                    counter += 1
                except Exception as e:
                    logs.append(f"Failed writing SRT entry for {file}: {e}")
                    append_log(log_file, f"Failed writing SRT entry for {file}: {e}", update_log_callback)
            else:
                no_text_msg = f"No text detected in {file}"
                logs.append(no_text_msg)
                append_log(log_file, no_text_msg, update_log_callback)
        except ValueError as ve:
            skip_msg = f"Skipping file {file}: {ve}"
            logs.append(skip_msg)
            append_log(log_file, skip_msg, update_log_callback)
        except Exception as e:
            err = f"Unexpected error processing {file}: {e}"
            logs.append(err)
            append_log(log_file, err, update_log_callback)
    if appended_any:
        saved_msg = f"SRT file saved to {output_srt}"
        logs.append(saved_msg)
        append_log(log_file, saved_msg, update_log_callback)
    else:
        none_msg = f"No valid files processed in {image_folder}"
        logs.append(none_msg)
        append_log(log_file, none_msg, update_log_callback)

def process_images(image_dir, output_folder, json_path, recursive, use_rgb, update_log_callback=None):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = json_path
    try:
        client = vision.ImageAnnotatorClient()
    except Exception as e:
        client = None
    logs = []
    os.makedirs(output_folder, exist_ok=True)
    log_file = os.path.join(output_folder, "process.log")
    append_log(log_file, f"Processing started at {time.strftime('%Y-%m-%d %H:%M:%S')}", update_log_callback)

    if use_rgb:
        parent_dir = os.path.dirname(image_dir)
        rgb_folder = os.path.join(parent_dir, "RGBImages")
        if os.path.isdir(rgb_folder):
            append_log(log_file, f"Switching to RGBImages folder: {rgb_folder}", update_log_callback)
            image_dir = rgb_folder
        else:
            append_log(log_file, f"No RGBImages folder found in {parent_dir}, continuing with selected folder", update_log_callback)

    if recursive:
        txtimages_folders = [
            os.path.join(root, subdir)
            for root, dirs, _ in os.walk(image_dir)
            for subdir in dirs
            if subdir == "TXTImages"
        ]
        if not txtimages_folders:
            msg = f"No TXTImages folder found in {image_dir}"
            logs.append(msg)
            append_log(log_file, msg, update_log_callback)
        else:
            for txt_folder in txtimages_folders:
                parent_name = os.path.basename(os.path.dirname(txt_folder)) or "folder"
                output_srt = os.path.join(output_folder, f"{parent_name}_output.srt")
                generate_srt_for_folder(txt_folder, output_srt, client, logs, log_file, update_log_callback)
    else:
        output_srt = os.path.join(output_folder, "output.srt")
        generate_srt_for_folder(image_dir, output_srt, client, logs, log_file, update_log_callback)

    append_log(log_file, f"Processing completed at {time.strftime('%Y-%m-%d %H:%M:%S')}", update_log_callback)
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

def run_program(folder_entry, output_folder_entry, json_entry, recursive_var, rgb_var, log_text):
    image_dir = folder_entry.get()
    output_folder = output_folder_entry.get()
    json_path = json_entry.get()
    recursive = recursive_var.get()
    use_rgb = rgb_var.get()

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
                try:
                    log_text.insert(tk.END, new_log)
                    log_text.yview(tk.END)
                except Exception:
                    pass
            process_images(image_dir, output_folder, json_path, recursive, use_rgb, update_log)
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
    root.geometry("800x500")

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
    tk.Checkbutton(root, text="Process Multiple Folders (Folder Containing Folders Containing TXTImages)", variable=recursive_var).grid(row=3, column=1, padx=10, pady=5, sticky="w")

    rgb_var = tk.BooleanVar(value=False)
    tk.Checkbutton(root, text="Use RGBImages folder instead of selected folder", variable=rgb_var).grid(row=4, column=1, padx=10, pady=5, sticky="w")

    global run_button
    run_button = tk.Button(root, text="Convert", command=lambda: run_program(folder_entry, output_folder_entry, json_entry, recursive_var, rgb_var, log_text), bg="green", fg="white")
    run_button.grid(row=5, column=1, pady=20)

    global log_text
    log_text = tk.Text(root, width=95, height=15)
    log_text.grid(row=6, column=0, columnspan=3, padx=10, pady=10)

    root.mainloop()

if __name__ == "__main__":
    main()
