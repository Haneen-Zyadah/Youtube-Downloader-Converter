import tkinter as tk
from tkinter import messagebox, filedialog, ttk
from yt_dlp import YoutubeDL
from PIL import Image, ImageTk
import requests
from io import BytesIO

# Global variables
formats_list = []
format_map = {}

# Download function
def download_video():
    url = url_entry.get().strip()
    if not url:
        messagebox.showerror("Error", "Please enter a video URL.")
        return

    selected = resolution_combobox.get()
    if not selected or selected not in format_map:
        messagebox.showerror("Error", "Please select a resolution.")
        return

    format_id = format_map[selected]
    download_dir = filedialog.askdirectory(title="Choose Download Folder")
    if not download_dir:
        return

    try:
        if is_mp3.get():
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': f'{download_dir}/%(title)s.%(ext)s',
                'ffmpeg_location': './ffmpeg',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'quiet': True,
            }
        else:
            ydl_opts = {
                'format': format_id,
                'outtmpl': f'{download_dir}/%(title)s.%(ext)s',
                'quiet': True,
            }

        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        msg = "MP3" if is_mp3.get() else "Video"
        messagebox.showinfo("Success", f"{msg} downloaded to:\n{download_dir}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to download:\n{e}")


# Show video info
def fetch_video_info():
    url = url_entry.get().strip()
    if not url:
        messagebox.showerror("Error", "Please enter a video URL.")
        return

    try:
        with YoutubeDL({"quiet": True}) as ydl:
            info = ydl.extract_info(url, download=False)

        title_label.config(text=f"Title: {info.get('title', 'N/A')}")
        author_label.config(text=f"Author: {info.get('uploader', 'N/A')}")
        duration_label.config(text=f"Duration: {info.get('duration', 'N/A')} seconds")

        # Get and display thumbnail
        thumb_url = info.get("thumbnail")
        if thumb_url:
            response = requests.get(thumb_url)
            img_data = Image.open(BytesIO(response.content))
            img_data = img_data.resize((320, 180))  # Resize thumbnail
            photo = ImageTk.PhotoImage(img_data)
            thumbnail_label.config(image=photo)
            thumbnail_label.image = photo

        # Prepare resolution options
        formats = info.get("formats", [])
        formats_list.clear()
        format_map.clear()

        for f in formats:
            if f.get('vcodec') != 'none' and f.get('acodec') != 'none' and f.get('height'):
                label = f"{f['height']}p - {f['ext']}"
                if label not in format_map:
                    formats_list.append(label)
                    format_map[label] = f["format_id"]

        if formats_list:
            resolution_combobox["values"] = formats_list
            resolution_combobox.current(0)
            resolution_combobox.config(state="readonly")
        else:
            resolution_combobox.set("No resolutions found")
            resolution_combobox.config(state="disabled")

    except Exception as e:
        messagebox.showerror("Error", f"Failed to fetch video info:\n{e}")


# GUI Setup
root = tk.Tk()
root.title("YouTube Video Downloader")
root.geometry("420x580")
root.resizable(False, False)
is_mp3 = tk.BooleanVar()  # For the MP3 checkbox

tk.Label(root, text="Enter YouTube Video URL:", font=("Arial", 12)).pack(pady=10)
url_entry = tk.Entry(root, width=50)
url_entry.pack(pady=5)

tk.Button(root, text="Show Info", command=fetch_video_info, bg="blue", fg="white").pack(pady=10)

title_label = tk.Label(root, text="", font=("Arial", 10))
title_label.pack(pady=5)

author_label = tk.Label(root, text="", font=("Arial", 10))
author_label.pack(pady=5)

duration_label = tk.Label(root, text="", font=("Arial", 10))
duration_label.pack(pady=5)

thumbnail_label = tk.Label(root)
thumbnail_label.pack(pady=10)

tk.Label(root, text="Choose Resolution:", font=("Arial", 10)).pack()
resolution_combobox = ttk.Combobox(root, state="disabled", width=30)
resolution_combobox.pack(pady=5)

tk.Checkbutton(root, text="Convert to MP3", variable=is_mp3).pack(pady=5)

tk.Button(root, text="Download", command=download_video, bg="green", fg="white").pack(pady=15)

root.mainloop()
