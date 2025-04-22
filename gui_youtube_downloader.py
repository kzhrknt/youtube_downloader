import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import yt_dlp

def fetch_resolutions(url):
    ydl_opts = {'listformats': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=False)
        formats = info_dict.get('formats', [])
        resolutions = [f"{f['format_id']} - {f['format_note']}" for f in formats if 'format_note' in f]
    return resolutions

def download_video(url, format_id, output_path):
    # Ask for the file name with the video title as the default
    file_name = simpledialog.askstring("File Name", "Enter file name:", initialvalue="%(title)s")
    if not file_name:
        return

    ydl_opts = {
        'format': f'{format_id}+bestaudio/best',
        'outtmpl': f'{output_path}/{file_name}.%(ext)s',
        'merge_output_format': 'mp4',
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        messagebox.showinfo("Success", "Download completed!")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

def start_download():
    url = url_entry.get()
    format_id = resolution_var.get().split(' - ')[0]
    output_path = filedialog.askdirectory()
    if not output_path:
        return
    download_video(url, format_id, output_path)

def update_resolutions():
    url = url_entry.get()
    resolutions = fetch_resolutions(url)
    resolution_var.set('')
    resolution_menu['values'] = resolutions

app = tk.Tk()
app.title("YouTube Downloader")

tk.Label(app, text="YouTube URL:").grid(row=0, column=0, padx=10, pady=10)
url_entry = tk.Entry(app, width=50)
url_entry.grid(row=0, column=1, padx=10, pady=10)

tk.Button(app, text="Fetch Resolutions", command=update_resolutions).grid(row=0, column=2, padx=10, pady=10)

tk.Label(app, text="Resolution:").grid(row=1, column=0, padx=10, pady=10)
resolution_var = tk.StringVar()
resolution_menu = ttk.Combobox(app, textvariable=resolution_var, width=47)
resolution_menu.grid(row=1, column=1, padx=10, pady=10)

tk.Button(app, text="Download", command=start_download).grid(row=2, column=1, pady=20)

app.mainloop()
