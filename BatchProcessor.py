import os
import time
import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import subprocess
import json
import shutil

# Global configuration for the lens_scan CLI executable
CLI_PATH = "lens_scan"

# Calculate paths relative to the directory of this script (BatchProcessor.py)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_FOLDER_PATH = os.path.normpath(os.path.join(SCRIPT_DIR, "PutVideosInHere", "output"))
DEFAULT_OUTPUT_PATH = SCRIPT_DIR


def parse_filename(filename):
    base_name = filename.rsplit(".", 1)[0]
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


def ocr_with_lens_scan(image_path, cli_path, log=None, max_retries=5):
    encodings_to_try = ["utf-8", "gbk", "gb2312", "gb18030"]

    # Build environmental overrides
    custom_env = os.environ.copy()
    
    # 1. Force Python inside lens_scan to print stdout/stderr using UTF-8
    custom_env["PYTHONIOENCODING"] = "utf-8"
    
    # 2. Inject Windows System32 into the environment so 'chcp' can be found
    system32_path = r"C:\Windows\System32"
    if system32_path not in custom_env.get("PATH", ""):
        custom_env["PATH"] = system32_path + os.pathsep + custom_env.get("PATH", "")

    for attempt in range(1, max_retries + 1):
        start = time.time()

        try:
            print(f"\n[{attempt}/{max_retries}] OCR: {os.path.basename(image_path)}")

            result = subprocess.run(
                [cli_path, image_path],
                capture_output=True,
                timeout=60,
                env=custom_env, # Passes the UTF-8 environmental overrides
            )

            elapsed = time.time() - start

            print(f"Finished in {elapsed:.2f}s")
            print(f"Return code: {result.returncode}")
            print(f"stdout bytes: {len(result.stdout)}")
            print(f"stderr bytes: {len(result.stderr)}")

            if result.stderr:
                try:
                    print("stderr:")
                    print(result.stderr.decode("utf-8", errors="replace"))
                except Exception:
                    print(result.stderr)

            if result.returncode != 0:
                print("Non-zero exit code.")
                if attempt < max_retries:
                    print("Retrying...")
                    time.sleep(5)
                    continue
                return ""

            if not result.stdout:
                print("stdout was empty.")
                if attempt < max_retries:
                    print("Retrying...")
                    time.sleep(5)
                    continue
                return ""

            raw = result.stdout

            text = None
            for enc in encodings_to_try:
                try:
                    decoded = raw.decode(enc)
                    if "\ufffd" not in decoded:
                        text = decoded
                        print(f"Decoded using {enc}")
                        break
                except Exception:
                    pass

            if text is None:
                text = raw.decode("utf-8", errors="replace")
                print("Decoded using utf-8 (replace)")

            print("Raw output:")
            print("=" * 60)
            print(text[:1000])
            print("=" * 60)

            lines = text.strip().splitlines()
            cleaned = []

            for line in lines:
                stripped = line.strip()

                if stripped.lower() in ("ocr results:", "::"):
                    continue

                if "failed to set console to utf-8" in stripped.lower():
                    continue

                stripped = stripped.strip(":").strip()

                if stripped:
                    cleaned.append(stripped)

            final = "\n".join(cleaned)

            print(f"Final OCR length: {len(final)}")

            if final:
                print("OCR succeeded.")
            else:
                print("OCR returned only headers/blank lines.")

            return final

        except subprocess.TimeoutExpired:
            elapsed = time.time() - start
            print(f"TIMEOUT after {elapsed:.2f}s")

            if attempt < max_retries:
                print("Retrying...")
                time.sleep(5)
            else:
                print("Giving up.")
                return ""

        except Exception as e:
            print(f"Exception: {e}")

            if attempt < max_retries:
                print("Retrying...")
                time.sleep(5)
            else:
                return ""

    return ""


def generate_srt_for_folder(
    image_folder, output_srt, cli_path, log_file, update_log_callback
):
    counter = 1
    output_srt = get_unique_filename(output_srt)
    files = sorted(
        f
        for f in os.listdir(image_folder)
        if f.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".webp"))
    )
    total = len(files)

    for idx, file in enumerate(files, 1):
        try:
            start_ts, end_ts = parse_filename(file)
            start_time = format_timestamp(start_ts)
            end_time = format_timestamp(end_ts)

            image_path = os.path.join(image_folder, file)
            text = ocr_with_lens_scan(image_path, cli_path)

            if text:
                with open(output_srt, "a", encoding="utf-8") as srt:
                    srt.write(f"{counter}\n{start_time} --> {end_time}\n{text}\n\n")

                append_log(
                    log_file,
                    f"[{idx}/{total}] Wrote subtitle #{counter} | "
                    f"{start_time} --> {end_time}\n{text}",
                    update_log_callback,
                )
                counter += 1
            else:
                append_log(
                    log_file,
                    f"[{idx}/{total}] OCR EMPTY | {start_time} --> {end_time} | {file}",
                    update_log_callback,
                )

        except Exception as e:
            append_log(
                log_file,
                f"[{idx}/{total}] Skipping {file}: {e}",
                update_log_callback,
            )


def process_images(base_dir, output_dir, cli_path, recursive, use_rgb, cb):
    if not shutil.which(cli_path) and not os.path.isfile(cli_path):
        raise FileNotFoundError(f"lens_scan executable not found. Please ensure '{cli_path}' is installed or present in the execution folder.")

    log_file = os.path.join(output_dir, "process.log")
    append_log(
        log_file,
        f"Processing started at {time.strftime('%Y-%m-%d %H:%M:%S')}",
        cb,
    )

    if recursive:
        txt_folders = [
            os.path.join(r, d)
            for r, ds, _ in os.walk(base_dir)
            for d in ds
            if d == "TXTImages"
        ]
        if not txt_folders:
            raise RuntimeError("No TXTImages folders found")

        for txt in txt_folders:
            img_folder = resolve_rgb_folder(txt) if use_rgb else txt
            out_name = os.path.basename(os.path.dirname(txt)) + "_output.srt"
            generate_srt_for_folder(
                img_folder,
                os.path.join(output_dir, out_name),
                cli_path,
                log_file,
                cb,
            )
    else:
        img_folder = resolve_rgb_folder(base_dir) if use_rgb else base_dir
        generate_srt_for_folder(
            img_folder,
            os.path.join(output_dir, "output.srt"),
            cli_path,
            log_file,
            cb,
        )

    append_log(log_file, "Processing completed", cb)


def run_program(folder_e, out_e, rec_v, rgb_v, log):
    folder = folder_e.get()
    out = out_e.get()

    if not folder or not out:
        messagebox.showwarning("Warning", "Please fill in all fields.")
        return

    run_button.config(state=tk.DISABLED)
    log.config(state=tk.NORMAL)
    log.delete(1.0, tk.END)
    log.config(state=tk.DISABLED)

    def thread():
        try:
            process_images(
                folder,
                out,
                CLI_PATH,
                rec_v.get(),
                rgb_v.get(),
                lambda t: write_log(log, t),
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


def main():
    root = tk.Tk()
    root.geometry("850x520")
    root.title("Image → SRT OCR (Lens Scan)")

    # Row 0: Folder Selection
    tk.Label(root, text="Folder").grid(row=0, column=0, sticky="w", padx=5)
    folder_e = tk.Entry(root, width=60)
    folder_e.grid(row=0, column=1)
    # Set the default relative video folder
    folder_e.insert(0, DEFAULT_FOLDER_PATH)
    tk.Button(root, text="Browse", command=lambda: browse_dir(folder_e)).grid(
        row=0, column=2, padx=5
    )

    # Row 1: Output Folder Selection
    tk.Label(root, text="Output").grid(row=1, column=0, sticky="w", padx=5)
    out_e = tk.Entry(root, width=60)
    out_e.grid(row=1, column=1)
    # Set the default current directory folder
    out_e.insert(0, DEFAULT_OUTPUT_PATH)
    tk.Button(root, text="Browse", command=lambda: browse_dir(out_e)).grid(
        row=1, column=2, padx=5
    )

    # Variables for options
    rec_v = tk.BooleanVar(value=True)  # Checked/True by default
    rgb_v = tk.BooleanVar()

    # Row 2: Recursive Folder Option
    tk.Checkbutton(
        root,
        text="Process Multiple Folders (Folder containing folders containing TXTImages)",
        variable=rec_v,
    ).grid(row=2, column=1, sticky="w")
    
    # Row 3: RGB vs TXT option
    tk.Checkbutton(
        root,
        text="Use RGBImages instead of TXTImages",
        variable=rgb_v,
    ).grid(row=3, column=1, sticky="w")

    # Row 4: Run execution button
    global run_button
    run_button = tk.Button(
        root,
        text="Convert",
        bg="green",
        fg="white",
        command=lambda: run_program(folder_e, out_e, rec_v, rgb_v, log),
    )
    run_button.grid(row=4, column=1, pady=10)

    # Row 5: Log Console Widget
    global log
    log = tk.Text(root, width=100, height=15, state=tk.DISABLED)
    log.grid(row=5, column=0, columnspan=3)

    root.mainloop()


if __name__ == "__main__":
    main()