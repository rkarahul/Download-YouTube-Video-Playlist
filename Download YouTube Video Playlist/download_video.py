import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pytube import YouTube, Playlist
import threading

class YouTubeDownloader:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Video Downloader")
        self.root.geometry("500x350")

        self.url_label = tk.Label(root, text="YouTube URL:")
        self.url_label.pack(pady=10)
        self.url_entry = tk.Entry(root, width=50)
        self.url_entry.pack(pady=10)

        self.download_type = tk.StringVar(value="video")
        self.video_radio = tk.Radiobutton(root, text="Single Video", variable=self.download_type, value="video", command=self.update_download_type)
        self.playlist_radio = tk.Radiobutton(root, text="Playlist", variable=self.download_type, value="playlist", command=self.update_download_type)
        self.video_radio.pack(pady=5)
        self.playlist_radio.pack(pady=5)

        self.quality_label = tk.Label(root, text="Select Quality:")
        self.quality_label.pack(pady=10)

        self.quality_combobox = ttk.Combobox(root, state="readonly")
        self.quality_combobox.pack(pady=10)

        self.download_button = tk.Button(root, text="Download", command=self.download_video)
        self.download_button.pack(pady=20)

        self.status_label = tk.Label(root, text="")
        self.status_label.pack(pady=10)

        self.url_entry.bind("<Return>", self.update_streams)
        self.url_entry.focus()

    def update_download_type(self):
        if self.download_type.get() == "video":
            self.quality_label.pack(pady=10)
            self.quality_combobox.pack(pady=10)
        else:
            self.quality_label.pack_forget()
            self.quality_combobox.pack_forget()

    def update_streams(self, event=None):
        url = self.url_entry.get()
        if not url:
            messagebox.showwarning("Warning", "Please enter a URL.")
            return

        if self.download_type.get() == "video":
            threading.Thread(target=self.fetch_video_streams, args=(url,)).start()

    def fetch_video_streams(self, url):
        try:
            yt = YouTube(url)
            self.streams = yt.streams.filter(progressive=True).order_by('resolution').desc()
            quality_options = [f"{stream.resolution} - {stream.mime_type}" for stream in self.streams]

            if quality_options:
                self.quality_combobox['values'] = quality_options
                self.quality_combobox.current(0)
            else:
                self.update_status("No available qualities found.")
                self.quality_combobox['values'] = []
        except Exception as e:
            self.update_status(f"Error: {str(e)}")

    def download_video(self):
        url = self.url_entry.get()
        if not url:
            messagebox.showwarning("Warning", "Please enter a URL.")
            return

        download_type = self.download_type.get()
        download_path = filedialog.askdirectory()
        if not download_path:
            return

        self.update_status(f"Selected download path: {download_path}")
        threading.Thread(target=self.download_task, args=(url, download_path, download_type)).start()

    def download_task(self, url, download_path, download_type):
        try:
            if download_type == "video":
                self.download_single_video(url, download_path)
            elif download_type == "playlist":
                self.download_playlist(url, download_path)
        except Exception as e:
            self.update_status(f"Error: {str(e)}")

    def download_single_video(self, url, download_path):
        try:
            selected_quality = self.quality_combobox.get().split(' - ')[0]  # Extract selected quality (e.g., "720p")
            yt = YouTube(url)
            stream = self.get_best_available_stream(yt, selected_quality)
            if stream:
                self.update_status(f"Downloading single video to {download_path}...")
                stream.download(output_path=download_path)
                self.update_status(f"Video downloaded successfully! Saved to: {download_path}")
                messagebox.showinfo("Success", f"Video downloaded successfully!\nSaved to: {download_path}")
            else:
                self.update_status(f"{selected_quality} quality not available for this video. Downloading default quality...")
                default_stream = yt.streams.filter(progressive=True).order_by('resolution').desc().first()
                if default_stream:
                    default_stream.download(output_path=download_path)
                    self.update_status(f"Video downloaded successfully at default quality! Saved to: {download_path}")
                    messagebox.showinfo("Success", f"Video downloaded successfully at default quality!\nSaved to: {download_path}")
                else:
                    self.update_status("No suitable video streams available.")
        except Exception as e:
            self.update_status(f"Download failed: {str(e)}")

    def download_playlist(self, url, download_path):
        try:
            playlist = Playlist(url)
            self.update_status(f"Downloading playlist: {playlist.title}")
            for video in playlist.videos:
                try:
                    yt = YouTube(video.watch_url)
                    stream = self.get_best_available_stream(yt, "720p")
                    if stream:
                        self.update_status(f"Downloading video: {video.title} to {download_path}")
                        stream.download(output_path=download_path)
                    else:
                        self.update_status(f"720p quality not available for {video.title}. Downloading default quality...")
                        default_stream = yt.streams.filter(progressive=True).order_by('resolution').desc().first()
                        if default_stream:
                            default_stream.download(output_path=download_path)
                        else:
                            self.update_status(f"No suitable video streams available for {video.title}.")
                except Exception as e:
                    self.update_status(f"Failed to download {video.title}: {str(e)}")
            self.update_status(f"Playlist downloaded successfully! Saved to: {download_path}")
            messagebox.showinfo("Success", f"Playlist downloaded successfully!\nSaved to: {download_path}")
        except Exception as e:
            self.update_status(f"Error: {str(e)}")
            messagebox.showerror("Error", str(e))

    def get_best_available_stream(self, yt, preferred_resolution):
        # Filter streams by progressive (non-DASH) and preferred resolution
        streams = yt.streams.filter(progressive=True, res=preferred_resolution).order_by('resolution').desc()
        # Check if any streams match preferred resolution
        if streams:
            return streams.first()
        else:
            return None

    def update_status(self, message):
        self.status_label.config(text=message)
        self.root.update_idletasks()

if __name__ == "__main__":
    root = tk.Tk()
    app = YouTubeDownloader(root)
    root.mainloop()

# print("888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888")


