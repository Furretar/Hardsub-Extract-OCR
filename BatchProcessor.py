import os
import time
import tkinter as tk
from tkinter import filedialog, messagebox
from google.cloud import vision
import threading

def parse_filename(filename):
    base_name = filename.rsplit('.', 1)[0]
    timestamps = base_name.split("__")
    start_ts = timestamps[0]
    end_ts = "_".join(timestamps[1].split("_")[:4])
    return start_ts, end_ts

def format_timestamp(timestamp):
    h, m, s, ms = map(int, timestamp.split("_"))
    return f"{h:02}:{m:02}:{s:02},{ms:03}"

def get_unique_filename(path):
    base, ext = os.path.splitext(path)
    i = 1
    out = path
    while os.path.exists(out):
        out = f"{base}_{i}{ext}"
        i += 1
    return out

log_lock = threading.Lock()

def write_log(widget, text):
    at_bottom = widget.yview()[1] == 1.0
    widget.config(state=tk.NORMAL)
    widget.insert(tk.END, text)
    if at_bottom:
        widget.yview(tk.END)
    widget.config(state=tk.DISABLED)

def append_log(log_file, text, cb=None):
    with log_lock:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(text + "\n")
    if cb:
        cb(text + "\n")

def resolve_rgb_folder(txt_folder):
    parent = os.path.dirname(txt_folder)
    rgb = os.path.join(parent, "RGBImages")
    if not os.path.isdir(rgb):
        raise FileNotFoundError(f"RGBImages folder not found next to:\n{txt_folder}")
    return rgb

def generate_srt_for_folder(image_folder, output_srt, client, log_file, update_log_callback):
    counter = 1
    output_srt = get_unique_filename(output_srt)
    for file in sorted(os.listdir(image_folder)):
        if not file.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".webp")):
            continue
        try:
            start_ts, end_ts = parse_filename(file)
            start_time = format_timestamp(start_ts)
            end_time = format_timestamp(end_ts)

            with open(os.path.join(image_folder, file), "rb") as f:
                image = vision.Image(content=f.read())

            while True:
                try:
                    response = client.text_detection(image=image)
                    break
                except Exception as e:
                    append_log(
                        log_file,
                        f"Connection lost, retrying for {file}: {e}",
                        update_log_callback
                    )
                    time.sleep(10)
                    client = vision.ImageAnnotatorClient()

            if response.text_annotations:
                text = response.text_annotations[0].description.strip()

                with open(output_srt, "a", encoding="utf-8") as srt:
                    srt.write(
                        f"{counter}\n"
                        f"{start_time} --> {end_time}\n"
                        f"{text}\n\n"
                    )

                append_log(
                    log_file,
                    f"Wrote subtitle #{counter} | {start_time} --> {end_time}\n{text}",
                    update_log_callback
                )

                counter += 1
            else:
                append_log(
                    log_file,
                    f"No text detected | {start_time} --> {end_time} | {file}",
                    update_log_callback
                )

        except Exception as e:
            append_log(
                log_file,
                f"Skipping {file}: {e}",
                update_log_callback
            )

def process_images(base_dir, output_dir, json_path, recursive, use_rgb, cb):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = json_path
    client = vision.ImageAnnotatorClient()
    log_file = os.path.join(output_dir, "process.log")
    append_log(log_file, f"Processing started at {time.strftime('%Y-%m-%d %H:%M:%S')}", cb)

    if recursive:
        txt_folders = [
            os.path.join(r, d)
            for r, ds, _ in os.walk(base_dir)
            for d in ds if d == "TXTImages"
        ]
        if not txt_folders:
            raise RuntimeError("No TXTImages folders found")

        for txt in txt_folders:
            img_folder = resolve_rgb_folder(txt) if use_rgb else txt
            out_name = os.path.basename(os.path.dirname(txt)) + "_output.srt"
            generate_srt_for_folder(img_folder, os.path.join(output_dir, out_name), client, log_file, cb)
    else:
        img_folder = resolve_rgb_folder(base_dir) if use_rgb else base_dir
        generate_srt_for_folder(img_folder, os.path.join(output_dir, "output.srt"), client, log_file, cb)

    append_log(log_file, "Processing completed", cb)

def run_program(folder_e, out_e, json_e, rec_v, rgb_v, log):
    folder = folder_e.get()
    out = out_e.get()
    jsonp = json_e.get()

    run_button.config(state=tk.DISABLED)
    log.config(state=tk.NORMAL)
    log.delete(1.0, tk.END)
    log.config(state=tk.DISABLED)

    def thread():
        try:
            process_images(
                folder, out, jsonp,
                rec_v.get(), rgb_v.get(),
                lambda t: write_log(log, t)
            )
        except Exception as e:
            messagebox.showerror("Error", str(e))
            write_log(log, str(e) + "\n")
        finally:
            run_button.config(state=tk.NORMAL)

    threading.Thread(target=thread, daemon=True).start()

def browse_dir(e):
    d = filedialog.askdirectory()
    if d:
        e.delete(0, tk.END)
        e.insert(0, d)

def browse_file(e):
    f = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
    if f:
        e.delete(0, tk.END)
        e.insert(0, f)

def main():
    root = tk.Tk()
    root.geometry("850x520")
    root.title("Image → SRT OCR")

    tk.Label(root, text="Folder").grid(row=0, column=0, sticky="w")
    folder_e = tk.Entry(root, width=60)
    folder_e.grid(row=0, column=1)
    tk.Button(root, text="Browse", command=lambda: browse_dir(folder_e)).grid(row=0, column=2)

    tk.Label(root, text="Output").grid(row=1, column=0, sticky="w")
    out_e = tk.Entry(root, width=60)
    out_e.grid(row=1, column=1)
    tk.Button(root, text="Browse", command=lambda: browse_dir(out_e)).grid(row=1, column=2)

    tk.Label(root, text="JSON").grid(row=2, column=0, sticky="w")
    json_e = tk.Entry(root, width=60)
    json_e.grid(row=2, column=1)
    tk.Button(root, text="Browse", command=lambda: browse_file(json_e)).grid(row=2, column=2)

    rec_v = tk.BooleanVar()
    rgb_v = tk.BooleanVar()

    tk.Checkbutton(root, text="Process Multiple Folders (TXTImages)", variable=rec_v).grid(row=3, column=1, sticky="w")
    tk.Checkbutton(root, text="Use RGBImages instead of TXTImages", variable=rgb_v).grid(row=4, column=1, sticky="w")

    global run_button
    run_button = tk.Button(
        root, text="Convert", bg="green", fg="white",
        command=lambda: run_program(folder_e, out_e, json_e, rec_v, rgb_v, log)
    )
    run_button.grid(row=5, column=1, pady=10)

    global log
    log = tk.Text(root, width=100, height=15, state=tk.DISABLED)
    log.grid(row=6, column=0, columnspan=3)

    root.mainloop()

if __name__ == "__main__":
    main()
