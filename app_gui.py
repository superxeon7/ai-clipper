# File: gui_modern.py

import os
import sys
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from pathlib import Path
from datetime import datetime
import re

from main import AIClipper


class ModernButton(tk.Button):
    """Custom modern button with hover effect."""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.defaultBackground = self["background"]
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
    
    def on_enter(self, e):
        if self['state'] != 'disabled':
            self['background'] = self['activebackground']
    
    def on_leave(self, e):
        self['background'] = self.defaultBackground


class AIClipperModernGUI:
    """AI Clipper Modern Desktop Application."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("AI Clipper Pro")
        self.root.geometry("1100x800")
        self.root.configure(bg='#1a1a2e')
        
        # Style
        self.setup_styles()
        
        # Variables
        self.input_type = tk.StringVar(value="file")  # file or youtube
        self.video_path = tk.StringVar()
        self.youtube_url = tk.StringVar()
        self.status_text = tk.StringVar(value="Ready to process videos")
        self.progress_value = tk.DoubleVar(value=0)
        self.is_processing = False
        self.clipper = None
        self.result = None
        
        # Setup UI
        self._setup_ui()
        self._center_window()
        
        # Initialize AIClipper
        self._init_clipper()
    
    def setup_styles(self):
        """Setup modern styles."""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors
        self.colors = {
            'primary': '#9933FF',
            'primary_hover': '#7722CC',
            'success': '#00D9A3',
            'danger': '#FF4757',
            'warning': '#FFA502',
            'dark': '#1a1a2e',
            'darker': '#16213e',
            'light': '#FFFFFF',
            'gray': '#4a4a6a',
            'bg_card': '#0f3460'
        }
        
        # Progressbar style
        style.configure(
            "Custom.Horizontal.TProgressbar",
            troughcolor='#2d2d44',
            background=self.colors['primary'],
            bordercolor='#2d2d44',
            lightcolor=self.colors['primary'],
            darkcolor=self.colors['primary']
        )
    
    def _init_clipper(self):
        """Initialize AI Clipper."""
        try:
            self.log_message("⚡ Initializing AI Clipper...", "info")
            self.clipper = AIClipper(config_path="config.yaml")
            self.log_message("✓ AI Clipper ready!", "success")
            self.status_text.set("Ready to create viral clips")
        except Exception as e:
            self.log_message(f"✗ Error: {e}", "error")
            messagebox.showerror("Error", str(e))
    
    def _setup_ui(self):
        """Setup modern user interface."""
        
        # ==================== HEADER ====================
        header_frame = tk.Frame(self.root, bg=self.colors['primary'], height=120)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        # Logo/Title
        title_frame = tk.Frame(header_frame, bg=self.colors['primary'])
        title_frame.pack(expand=True)
        
        title_label = tk.Label(
            title_frame,
            text="✨ AI CLIPPER PRO",
            font=("Segoe UI", 32, "bold"),
            bg=self.colors['primary'],
            fg=self.colors['light']
        )
        title_label.pack()
        
        subtitle_label = tk.Label(
            title_frame,
            text="Transform long videos into viral shorts with AI magic",
            font=("Segoe UI", 12),
            bg=self.colors['primary'],
            fg='#E0D4FF'
        )
        subtitle_label.pack()
        
        # ==================== MAIN CONTAINER ====================
        main_container = tk.Frame(self.root, bg=self.colors['dark'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=30, pady=25)
        
        # Left Panel (Input & Settings)
        left_panel = tk.Frame(main_container, bg=self.colors['darker'], relief=tk.FLAT)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 15))
        
        # Right Panel (Progress & Log)
        right_panel = tk.Frame(main_container, bg=self.colors['darker'], width=350)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH)
        right_panel.pack_propagate(False)
        
        # ==================== LEFT PANEL ====================
        
        # Input Type Selection
        input_type_frame = tk.Frame(left_panel, bg=self.colors['darker'], pady=20, padx=25)
        input_type_frame.pack(fill=tk.X)
        
        tk.Label(
            input_type_frame,
            text="📥 Input Source",
            font=("Segoe UI", 14, "bold"),
            bg=self.colors['darker'],
            fg=self.colors['light']
        ).pack(anchor=tk.W, pady=(0, 15))
        
        # Radio buttons for input type
        radio_frame = tk.Frame(input_type_frame, bg=self.colors['darker'])
        radio_frame.pack(fill=tk.X)
        
        style_radio = {
            'font': ("Segoe UI", 11),
            'bg': self.colors['darker'],
            'fg': self.colors['light'],
            'selectcolor': self.colors['bg_card'],
            'activebackground': self.colors['darker'],
            'activeforeground': self.colors['primary']
        }
        
        self.file_radio = tk.Radiobutton(
            radio_frame,
            text="💾 Local Video File",
            variable=self.input_type,
            value="file",
            command=self._toggle_input_type,
            **style_radio
        )
        self.file_radio.pack(side=tk.LEFT, padx=(0, 30))
        
        self.youtube_radio = tk.Radiobutton(
            radio_frame,
            text="🌐 YouTube URL",
            variable=self.input_type,
            value="youtube",
            command=self._toggle_input_type,
            **style_radio
        )
        self.youtube_radio.pack(side=tk.LEFT)
        
        # Separator
        ttk.Separator(left_panel, orient='horizontal').pack(fill=tk.X, padx=25, pady=10)
        
        # File Input Section
        self.file_section = tk.Frame(left_panel, bg=self.colors['darker'], pady=15, padx=25)
        self.file_section.pack(fill=tk.X)
        
        tk.Label(
            self.file_section,
            text="Select Video File",
            font=("Segoe UI", 11),
            bg=self.colors['darker'],
            fg=self.colors['light']
        ).pack(anchor=tk.W, pady=(0, 8))
        
        file_input_frame = tk.Frame(self.file_section, bg=self.colors['darker'])
        file_input_frame.pack(fill=tk.X)
        
        self.video_entry = tk.Entry(
            file_input_frame,
            textvariable=self.video_path,
            font=("Segoe UI", 10),
            bg=self.colors['bg_card'],
            fg=self.colors['light'],
            insertbackground=self.colors['light'],
            relief=tk.FLAT,
            state="readonly"
        )
        self.video_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=10, padx=(0, 10))
        
        self.browse_btn = ModernButton(
            file_input_frame,
            text="📂 Browse",
            command=self._browse_video,
            bg=self.colors['primary'],
            fg=self.colors['light'],
            font=("Segoe UI", 10, "bold"),
            padx=20,
            pady=10,
            cursor="hand2",
            relief=tk.FLAT,
            activebackground=self.colors['primary_hover']
        )
        self.browse_btn.pack(side=tk.RIGHT)
        
        # YouTube Input Section
        self.youtube_section = tk.Frame(left_panel, bg=self.colors['darker'], pady=15, padx=25)
        
        tk.Label(
            self.youtube_section,
            text="YouTube Video URL",
            font=("Segoe UI", 11),
            bg=self.colors['darker'],
            fg=self.colors['light']
        ).pack(anchor=tk.W, pady=(0, 8))
        
        youtube_input_frame = tk.Frame(self.youtube_section, bg=self.colors['darker'])
        youtube_input_frame.pack(fill=tk.X)
        
        self.youtube_entry = tk.Entry(
            youtube_input_frame,
            textvariable=self.youtube_url,
            font=("Segoe UI", 10),
            bg=self.colors['bg_card'],
            fg=self.colors['light'],
            insertbackground=self.colors['light'],
            relief=tk.FLAT
        )
        self.youtube_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=10, padx=(0, 10))
        self.youtube_entry.insert(0, "https://youtube.com/watch?v=...")
        self.youtube_entry.bind("<FocusIn>", self._clear_youtube_placeholder)
        self.youtube_entry.bind("<FocusOut>", self._restore_youtube_placeholder)
        
        self.download_btn = ModernButton(
            youtube_input_frame,
            text="⬇️ Download",
            command=self._download_youtube,
            bg=self.colors['danger'],
            fg=self.colors['light'],
            font=("Segoe UI", 10, "bold"),
            padx=20,
            pady=10,
            cursor="hand2",
            relief=tk.FLAT,
            activebackground='#E63946'
        )
        self.download_btn.pack(side=tk.RIGHT)
        
        # Info label
        self.youtube_info = tk.Label(
            self.youtube_section,
            text="Paste a YouTube video URL and click Download",
            font=("Segoe UI", 9),
            bg=self.colors['darker'],
            fg=self.colors['gray']
        )
        self.youtube_info.pack(anchor=tk.W, pady=(8, 0))
        
        # Separator
        ttk.Separator(left_panel, orient='horizontal').pack(fill=tk.X, padx=25, pady=15)
        
        # Settings Section
        settings_frame = tk.Frame(left_panel, bg=self.colors['darker'], padx=25, pady=15)
        settings_frame.pack(fill=tk.X)
        
        tk.Label(
            settings_frame,
            text="⚙️ Processing Settings",
            font=("Segoe UI", 14, "bold"),
            bg=self.colors['darker'],
            fg=self.colors['light']
        ).pack(anchor=tk.W, pady=(0, 15))
        
        # Model Size
        model_frame = tk.Frame(settings_frame, bg=self.colors['darker'])
        model_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(
            model_frame,
            text="AI Model:",
            font=("Segoe UI", 11),
            bg=self.colors['darker'],
            fg=self.colors['light']
        ).pack(side=tk.LEFT, padx=(0, 15))
        
        self.model_var = tk.StringVar(value="small")
        models = [("Tiny (Fast)", "tiny"), ("Base", "base"), ("Small (Best)", "small"), ("Medium", "medium")]
        
        for text, value in models:
            rb = tk.Radiobutton(
                model_frame,
                text=text,
                variable=self.model_var,
                value=value,
                font=("Segoe UI", 10),
                bg=self.colors['darker'],
                fg=self.colors['light'],
                selectcolor=self.colors['bg_card'],
                activebackground=self.colors['darker']
            )
            rb.pack(side=tk.LEFT, padx=5)
        
        # Number of Clips
        clips_frame = tk.Frame(settings_frame, bg=self.colors['darker'])
        clips_frame.pack(fill=tk.X)
        
        tk.Label(
            clips_frame,
            text="Number of Clips:",
            font=("Segoe UI", 11),
            bg=self.colors['darker'],
            fg=self.colors['light']
        ).pack(side=tk.LEFT, padx=(0, 15))
        
        self.clips_var = tk.IntVar(value=5)
        clips_spin = tk.Spinbox(
            clips_frame,
            from_=1,
            to=10,
            textvariable=self.clips_var,
            width=5,
            font=("Segoe UI", 11),
            bg=self.colors['bg_card'],
            fg=self.colors['light'],
            relief=tk.FLAT,
            buttonbackground=self.colors['primary']
        )
        clips_spin.pack(side=tk.LEFT)
        
        # Process Button (BIG and CENTERED)
        button_container = tk.Frame(left_panel, bg=self.colors['darker'], pady=30)
        button_container.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.process_btn = ModernButton(
            button_container,
            text="🚀 START PROCESSING",
            command=self._start_processing,
            bg=self.colors['success'],
            fg=self.colors['light'],
            font=("Segoe UI", 16, "bold"),
            padx=60,
            pady=20,
            cursor="hand2",
            relief=tk.FLAT,
            activebackground='#00B386'
        )
        self.process_btn.pack(expand=True)
        
        # ==================== RIGHT PANEL ====================
        
        # Progress Section
        progress_frame = tk.Frame(right_panel, bg=self.colors['darker'], padx=20, pady=20)
        progress_frame.pack(fill=tk.X)
        
        tk.Label(
            progress_frame,
            text="📊 Progress",
            font=("Segoe UI", 13, "bold"),
            bg=self.colors['darker'],
            fg=self.colors['light']
        ).pack(anchor=tk.W, pady=(0, 15))
        
        # Status
        self.status_label = tk.Label(
            progress_frame,
            textvariable=self.status_text,
            font=("Segoe UI", 10),
            bg=self.colors['darker'],
            fg=self.colors['light'],
            wraplength=280,
            justify=tk.LEFT
        )
        self.status_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Progress bar
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            variable=self.progress_value,
            maximum=100,
            mode='determinate',
            style="Custom.Horizontal.TProgressbar"
        )
        self.progress_bar.pack(fill=tk.X, pady=(0, 8))
        
        # Percentage
        self.progress_label = tk.Label(
            progress_frame,
            text="0%",
            font=("Segoe UI", 12, "bold"),
            bg=self.colors['darker'],
            fg=self.colors['primary']
        )
        self.progress_label.pack(anchor=tk.E)
        
        # Log Section
        log_frame = tk.Frame(right_panel, bg=self.colors['darker'], padx=20, pady=10)
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(
            log_frame,
            text="📝 Activity Log",
            font=("Segoe UI", 13, "bold"),
            bg=self.colors['darker'],
            fg=self.colors['light']
        ).pack(anchor=tk.W, pady=(0, 10))
        
        # Log text with custom colors
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            height=20,
            font=("Consolas", 9),
            bg=self.colors['bg_card'],
            fg='#A0A0C0',
            wrap=tk.WORD,
            relief=tk.FLAT,
            padx=10,
            pady=10
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Configure log tags for colors
        self.log_text.tag_config("info", foreground="#00D9A3")
        self.log_text.tag_config("success", foreground="#00D9A3", font=("Consolas", 9, "bold"))
        self.log_text.tag_config("error", foreground="#FF4757", font=("Consolas", 9, "bold"))
        self.log_text.tag_config("warning", foreground="#FFA502")
        
        # Open Output Button
        self.open_output_btn = ModernButton(
            log_frame,
            text="📁 Open Output Folder",
            command=self._open_output_folder,
            bg=self.colors['primary'],
            fg=self.colors['light'],
            font=("Segoe UI", 11, "bold"),
            padx=30,
            pady=12,
            cursor="hand2",
            relief=tk.FLAT,
            state=tk.DISABLED,
            activebackground=self.colors['primary_hover']
        )
        self.open_output_btn.pack(fill=tk.X, pady=(15, 0))
        
        # Initial input type
        self._toggle_input_type()
    
    def _toggle_input_type(self):
        try:
            parent = self.file_section.master
            children = parent.winfo_children()

            # Cek apakah ada cukup children untuk pakai 'before'
            if len(children) > 3:
                target_widget = children[3]
                # Pastikan target_widget sudah dipack
                if str(target_widget) in parent.pack_slaves():
                    self.file_section.pack(fill=tk.X, before=target_widget)
                else:
                    self.file_section.pack(fill=tk.X)
            else:
                self.file_section.pack(fill=tk.X)

        except Exception as e:
            print("Error packing file_section, packing normally:", e)
            self.file_section.pack(fill=tk.X)

    
    def _clear_youtube_placeholder(self, event):
        """Clear YouTube placeholder."""
        if self.youtube_entry.get() == "https://youtube.com/watch?v=...":
            self.youtube_entry.delete(0, tk.END)
            self.youtube_entry.config(fg=self.colors['light'])
    
    def _restore_youtube_placeholder(self, event):
        """Restore YouTube placeholder."""
        if not self.youtube_entry.get():
            self.youtube_entry.insert(0, "https://youtube.com/watch?v=...")
            self.youtube_entry.config(fg=self.colors['gray'])
    
    def _center_window(self):
        """Center window on screen."""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def _browse_video(self):
        """Browse for video file."""
        if self.is_processing:
            messagebox.showwarning("Processing", "Please wait for current processing to complete")
            return
        
        filename = filedialog.askopenfilename(
            title="Select Video File",
            filetypes=[
                ("Video Files", "*.mp4 *.mov *.avi *.mkv *.webm"),
                ("All Files", "*.*")
            ]
        )
        
        if filename:
            self.video_path.set(filename)
            self.log_message(f"✓ Selected: {Path(filename).name}", "success")
    
    def _download_youtube(self):
        """Download YouTube video."""
        if self.is_processing:
            messagebox.showwarning("Processing", "Please wait for current processing to complete")
            return
        
        url = self.youtube_url.get()
        
        # Validate URL
        if not url or url == "https://youtube.com/watch?v=...":
            messagebox.showwarning("No URL", "Please enter a YouTube URL")
            return
        
        # Validate YouTube URL format
        youtube_regex = r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})'
        if not re.match(youtube_regex, url):
            messagebox.showerror("Invalid URL", "Please enter a valid YouTube URL")
            return
        
        # Check if yt-dlp is installed
        try:
            import yt_dlp
        except ImportError:
            if messagebox.askyesno(
                "Missing Dependency",
                "yt-dlp is required to download YouTube videos.\n\nInstall it now?\n\nCommand: pip install yt-dlp"
            ):
                self.log_message("Installing yt-dlp...", "info")
                os.system("pip install yt-dlp")
                messagebox.showinfo("Installation", "Please restart the application after installation")
            return
        
        # Download in thread
        self.log_message(f"⬇️ Downloading from YouTube...", "info")
        self.download_btn.config(state=tk.DISABLED, text="⏳ Downloading...")
        
        thread = threading.Thread(target=self._download_youtube_thread, args=(url,), daemon=True)
        thread.start()
    
    def _download_youtube_thread(self, url):
        """Download YouTube video in background."""
        try:
            import yt_dlp
            
            # Create downloads folder
            download_dir = "./downloads"
            os.makedirs(download_dir, exist_ok=True)
            
            # Download options
            ydl_opts = {
                'format': 'best[ext=mp4]',
                'outtmpl': os.path.join(download_dir, '%(title)s.%(ext)s'),
                'quiet': True,
                'no_warnings': True
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
            
            # Set as video path
            self.video_path.set(filename)
            
            self.log_message(f"✓ Downloaded: {Path(filename).name}", "success")
            messagebox.showinfo("Success", f"Video downloaded successfully!\n\n{Path(filename).name}")
            
            # Switch to file mode
            self.root.after(0, lambda: self.input_type.set("file"))
            self.root.after(0, self._toggle_input_type)
            
        except Exception as e:
            self.log_message(f"✗ Download failed: {e}", "error")
            self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to download video:\n\n{str(e)}"))
        
        finally:
            self.root.after(0, lambda: self.download_btn.config(state=tk.NORMAL, text="⬇️ Download"))
    
    def _start_processing(self):
        """Start video processing."""
        if self.is_processing:
            messagebox.showwarning("Processing", "Already processing a video")
            return
        
        # Check input
        if self.input_type.get() == "file":
            if not self.video_path.get():
                messagebox.showwarning("No Video", "Please select a video file first")
                return
            video_file = self.video_path.get()
        else:
            messagebox.showinfo("Download First", "Please download the YouTube video first")
            return
        
        # Confirm
        if not messagebox.askyesno(
            "Start Processing",
            f"Start processing this video?\n\nSettings:\n• Model: {self.model_var.get()}\n• Clips: {self.clips_var.get()}\n\nThis may take several minutes."
        ):
            return
        
        # Update config
        self.clipper.config['transcription']['model_size'] = self.model_var.get()
        self.clipper.config['ai_analysis']['top_n_clips'] = self.clips_var.get()
        
        # Disable controls
        self.is_processing = True
        self.process_btn.config(state=tk.DISABLED, text="⏳ PROCESSING...")
        self.browse_btn.config(state=tk.DISABLED)
        self.download_btn.config(state=tk.DISABLED)
        self.open_output_btn.config(state=tk.DISABLED)
        self.progress_value.set(0)
        
        # Clear log
        self.log_text.delete(1.0, tk.END)
        
        # Start processing
        thread = threading.Thread(target=self._process_video_thread, args=(video_file,), daemon=True)
        thread.start()
    
    def _process_video_thread(self, video_file):
        """Process video in background."""
        try:
            self.log_message("="*40, "info")
            self.log_message("🚀 Starting AI Clipper Pro", "info")
            self.log_message("="*40, "info")
            
            self.update_progress(5, "Initializing...")
            
            # Process
            result = self.clipper.process_video(video_file, output_dir=None)
            
            self.result = result
            
            if result.get('success'):
                self.update_progress(100, "Complete!")
                self.log_message("="*40, "success")
                self.log_message("✓ SUCCESS! All clips generated!", "success")
                self.log_message("="*40, "success")
                self.log_message(f"📁 Output: {result['output_directory']}", "info")
                self.log_message(f"🎬 Clips: {result['clips_generated']}", "info")
                
                self.root.after(0, lambda: self.open_output_btn.config(state=tk.NORMAL))
                
                self.root.after(0, lambda: messagebox.showinfo(
                    "🎉 Success!",
                    f"Processing complete!\n\n"
                    f"✓ Clips generated: {result['clips_generated']}\n"
                    f"✓ Modern animated subtitles\n"
                    f"✓ AI-generated captions\n\n"
                    f"Output: {Path(result['output_directory']).name}"
                ))
            else:
                raise Exception(result.get('error', 'Unknown error'))
                
        except Exception as e:
            self.log_message(f"✗ ERROR: {str(e)}", "error")
            self.update_progress(0, "Error occurred")
            self.root.after(0, lambda: messagebox.showerror("Error", f"Processing failed:\n\n{str(e)}"))
        
        finally:
            self.is_processing = False
            self.root.after(0, lambda: self.process_btn.config(state=tk.NORMAL, text="🚀 START PROCESSING"))
            self.root.after(0, lambda: self.browse_btn.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.download_btn.config(state=tk.NORMAL))
    
    def update_progress(self, value, status):
        """Update progress."""
        self.root.after(0, lambda: self.progress_value.set(value))
        self.root.after(0, lambda: self.status_text.set(status))
        self.root.after(0, lambda: self.progress_label.config(text=f"{int(value)}%"))
    
    def log_message(self, message, tag="info"):
        """Add message to log."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_line = f"[{timestamp}] {message}\n"
        
        self.root.after(0, lambda: self.log_text.insert(tk.END, log_line, tag))
        self.root.after(0, lambda: self.log_text.see(tk.END))
    
    def _open_output_folder(self):
        """Open output folder."""
        if self.result and 'output_directory' in self.result:
            output_dir = self.result['output_directory']
            
            if os.path.exists(output_dir):
                if sys.platform == 'win32':
                    os.startfile(output_dir)
                elif sys.platform == 'darwin':
                    os.system(f'open "{output_dir}"')
                else:
                    os.system(f'xdg-open "{output_dir}"')
            else:
                messagebox.showerror("Error", "Output folder not found")
        else:
            messagebox.showwarning("No Output", "No output available yet")


def main():
    """Run Modern GUI."""
    root = tk.Tk()
    app = AIClipperModernGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()