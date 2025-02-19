import cv2
import numpy as np
import random
from pathlib import Path
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from threading import Thread
from datetime import datetime

class VideoGeneratorUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Generator")
        self.root.geometry("900x800")
        
        # Variables
        self.input_path = tk.StringVar()
        self.num_versions = tk.IntVar(value=5)
        self.status_var = tk.StringVar(value="Ready")
        self.progress_var = tk.DoubleVar(value=0)
        
        # Effect variables
        self.speed_var = tk.BooleanVar(value=True)
        self.color_var = tk.BooleanVar(value=True)
        self.border_var = tk.BooleanVar(value=True)
        self.overlay_var = tk.BooleanVar(value=True)
        self.zoom_var = tk.BooleanVar(value=True)
        self.edge_var = tk.BooleanVar(value=True)
        
        # Effect parameters
        self.zoom_min = tk.DoubleVar(value=0.5)
        self.zoom_max = tk.DoubleVar(value=1.5)
        self.edge_threshold1 = tk.IntVar(value=100)
        self.edge_threshold2 = tk.IntVar(value=200)
        self.speed_min = tk.DoubleVar(value=0.5)
        self.speed_max = tk.DoubleVar(value=1.5)

        self.setup_ui()

    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Input file section
        ttk.Label(main_frame, text="Input Video:").grid(row=0, column=0, sticky=tk.W)
        ttk.Entry(main_frame, textvariable=self.input_path, width=50).grid(row=0, column=1, padx=5)
        ttk.Button(main_frame, text="Browse", command=self.browse_file).grid(row=0, column=2)

        # Parameters frame
        params_frame = ttk.LabelFrame(main_frame, text="Generation Parameters", padding="10")
        params_frame.grid(row=1, column=0, columnspan=3, pady=10, sticky=(tk.W, tk.E))

        # Number of versions
        ttk.Label(params_frame, text="Number of versions:").grid(row=0, column=0, sticky=tk.W)
        ttk.Entry(params_frame, textvariable=self.num_versions, width=10).grid(row=0, column=1, sticky=tk.W)

        # Effect toggles
        effects_frame = ttk.LabelFrame(params_frame, text="Effects", padding="5")
        effects_frame.grid(row=1, column=0, columnspan=2, pady=5, sticky=(tk.W, tk.E))
        
        ttk.Checkbutton(effects_frame, text="Speed Modification", variable=self.speed_var).grid(row=0, column=0, sticky=tk.W)
        ttk.Checkbutton(effects_frame, text="Color Modification", variable=self.color_var).grid(row=0, column=1, sticky=tk.W)
        ttk.Checkbutton(effects_frame, text="Border Modification", variable=self.border_var).grid(row=1, column=0, sticky=tk.W)
        ttk.Checkbutton(effects_frame, text="Overlay Modification", variable=self.overlay_var).grid(row=1, column=1, sticky=tk.W)

        # Speed controls
        speed_frame = ttk.LabelFrame(params_frame, text="Speed Settings", padding="5")
        speed_frame.grid(row=2, column=0, columnspan=2, pady=5, sticky=(tk.W, tk.E))
        
        ttk.Label(speed_frame, text="Min Speed:").grid(row=0, column=0, sticky=tk.W)
        ttk.Entry(speed_frame, textvariable=self.speed_min, width=10).grid(row=0, column=1)
        ttk.Label(speed_frame, text="Max Speed:").grid(row=0, column=2, sticky=tk.W)
        ttk.Entry(speed_frame, textvariable=self.speed_max, width=10).grid(row=0, column=3)

        # Zoom controls
        zoom_frame = ttk.LabelFrame(params_frame, text="Zoom Settings", padding="5")
        zoom_frame.grid(row=3, column=0, columnspan=2, pady=5, sticky=(tk.W, tk.E))
        
        ttk.Checkbutton(zoom_frame, text="Enable Zoom", variable=self.zoom_var).grid(row=0, column=0, sticky=tk.W)
        ttk.Label(zoom_frame, text="Min Zoom:").grid(row=1, column=0, sticky=tk.W)
        ttk.Entry(zoom_frame, textvariable=self.zoom_min, width=10).grid(row=1, column=1)
        ttk.Label(zoom_frame, text="Max Zoom:").grid(row=1, column=2, sticky=tk.W)
        ttk.Entry(zoom_frame, textvariable=self.zoom_max, width=10).grid(row=1, column=3)

        # Edge Detection controls
        edge_frame = ttk.LabelFrame(params_frame, text="Edge Detection", padding="5")
        edge_frame.grid(row=4, column=0, columnspan=2, pady=5, sticky=(tk.W, tk.E))
        
        ttk.Checkbutton(edge_frame, text="Enable Edge Detection", variable=self.edge_var).grid(row=0, column=0, sticky=tk.W)
        ttk.Label(edge_frame, text="Threshold1:").grid(row=1, column=0, sticky=tk.W)
        ttk.Entry(edge_frame, textvariable=self.edge_threshold1, width=10).grid(row=1, column=1)
        ttk.Label(edge_frame, text="Threshold2:").grid(row=1, column=2, sticky=tk.W)
        ttk.Entry(edge_frame, textvariable=self.edge_threshold2, width=10).grid(row=1, column=3)

        # Generate button
        ttk.Button(main_frame, text="Generate Videos", command=self.start_generation).grid(row=2, column=0, columnspan=3, pady=10)

        # Progress bar
        self.progress = ttk.Progressbar(main_frame, length=300, mode='determinate', variable=self.progress_var)
        self.progress.grid(row=3, column=0, columnspan=3, pady=5)

        # Status label
        ttk.Label(main_frame, textvariable=self.status_var).grid(row=4, column=0, columnspan=3)

        # Results text area
        self.result_text = tk.Text(main_frame, height=15, width=70)
        self.result_text.grid(row=5, column=0, columnspan=3, pady=10)

    def browse_file(self):
        filename = filedialog.askopenfilename(
            filetypes=[
                ("Video files", "*.mp4 *.avi *.mov *.mkv"),
                ("All files", "*.*")
            ]
        )
        if filename:
            self.input_path.set(filename)

    def start_generation(self):
        if not self.input_path.get():
            messagebox.showerror("Error", "Please select an input video file")
            return

        # Disable generate button during processing
        for widget in self.root.winfo_children():
            if isinstance(widget, ttk.Button):
                widget.configure(state='disabled')

        # Start generation in a separate thread
        Thread(target=self.generate_videos, daemon=True).start()

    def generate_videos(self):
        try:
            modifier = VideoModifier(
                self.input_path.get(),
                self.speed_var.get(),
                self.color_var.get(),
                self.border_var.get(),
                self.overlay_var.get(),
                self.zoom_var.get(),
                self.edge_var.get(),
                self.zoom_min.get(),
                self.zoom_max.get(),
                self.edge_threshold1.get(),
                self.edge_threshold2.get(),
                self.speed_min.get(),
                self.speed_max.get(),
                self.update_progress,
                self.update_status
            )
            modifier.generate_multiple_versions(self.num_versions.get())
            
            self.status_var.set("Generation completed!")
            messagebox.showinfo("Success", "Video generation completed successfully!")
        except Exception as e:
            self.status_var.set(f"Error: {str(e)}")
            messagebox.showerror("Error", str(e))
        finally:
            # Re-enable generate button
            for widget in self.root.winfo_children():
                if isinstance(widget, ttk.Button):
                    widget.configure(state='normal')
            self.progress_var.set(0)

    def update_progress(self, value):
        self.progress_var.set(value)
        self.root.update_idletasks()

    def update_status(self, message):
        self.result_text.insert(tk.END, message + "\n")
        self.result_text.see(tk.END)
        self.root.update_idletasks()

class VideoModifier:
    def __init__(self, input_video_path, use_speed=True, use_color=True, 
             use_border=True, use_overlay=True, use_zoom=True, use_edge=True,
             zoom_min=0.5, zoom_max=1.5, edge_threshold1=100, edge_threshold2=200,
             speed_min=0.5, speed_max=2.0, progress_callback=None, 
             status_callback=None):
        self.input_path = input_video_path
        self.use_speed = use_speed
        self.use_color = use_color
        self.use_border = use_border
        self.use_overlay = use_overlay
        self.use_zoom = use_zoom
        self.use_edge = use_edge
        self.zoom_min = zoom_min
        self.zoom_max = zoom_max
        self.edge_threshold1 = edge_threshold1
        self.edge_threshold2 = edge_threshold2
        self.speed_min = speed_min
        self.speed_max = speed_max
        self.progress_callback = progress_callback
        self.status_callback = status_callback
        
        self.cap = cv2.VideoCapture(input_video_path)
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.frame_count = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))

    def apply_zoom(self, frame, zoom_factor):
        """Apply zoom to frame"""
        if zoom_factor == 1.0:
            return frame

        height, width = frame.shape[:2]
        center_x, center_y = width // 2, height // 2

        # Calculate new dimensions
        new_width = int(width / zoom_factor)
        new_height = int(height / zoom_factor)

        # Calculate crop ranges
        start_x = center_x - new_width // 2
        start_y = center_y - new_height // 2
        end_x = start_x + new_width
        end_y = start_y + new_height

        # Ensure crop coordinates are within bounds
        start_x = max(0, start_x)
        start_y = max(0, start_y)
        end_x = min(width, end_x)
        end_y = min(height, end_y)

        # Crop and resize
        cropped = frame[start_y:end_y, start_x:end_x]
        return cv2.resize(cropped, (width, height), interpolation=cv2.INTER_LINEAR)

    def apply_edge_detection(self, frame):
        """Apply Canny edge detection"""
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Apply Canny edge detection
        edges = cv2.Canny(blurred, self.edge_threshold1, self.edge_threshold2)
        
        # Convert back to BGR for colored edge overlay
        edges_colored = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
        
        # Blend original frame with edges
        result = cv2.addWeighted(frame, 0.7, edges_colored, 0.3, 0)
        return result

    def generate_modified_video(self, output_path):
        # Random modifications within reasonable ranges
        speed_factor = random.uniform(self.speed_min, self.speed_max) if self.use_speed else 1.0
        zoom_factor = random.uniform(self.zoom_min, self.zoom_max) if self.use_zoom else 1.0
        
        hue_shift = random.randint(-15, 15) if self.use_color else 0  # Increased from 0-180
        saturation_factor = random.uniform(0.9, 1.1) if self.use_color else 1.0  # Wider range
        brightness_factor = random.uniform(0.9, 1.1) if self.use_color else 1.0  # New brightness modification
        
        border_size = random.randint(0, 50) if self.use_border else 0  # Increased from 0-50
        border_color = (
            random.randint(0, 255),
            random.randint(0, 255),
            random.randint(0, 255)
        ) if self.use_border else (0, 0, 0)

        # Create video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(
            output_path,
            fourcc,
            self.fps * speed_factor,
            (self.width, self.height)
        )

        frame_number = 0
        while self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
              break

            # Apply zoom if enabled
            if self.use_zoom:
              frame = self.apply_zoom(frame, zoom_factor)

            # Apply color modifications
            if self.use_color:
              hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
              hsv = hsv.astype(np.float32)
              
              hsv[:, :, 0] = (hsv[:, :, 0] + hue_shift) % 180
              hsv[:, :, 1] = np.clip(hsv[:, :, 1] * saturation_factor, 0, 255)
              hsv[:, :, 2] = np.clip(hsv[:, :, 2] * brightness_factor, 0, 255)
              
              hsv = hsv.astype(np.uint8)
              frame = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

            # Apply border
            if self.use_border and border_size > 0:
              frame = cv2.copyMakeBorder(
                  frame,
                  border_size, border_size, border_size, border_size,
                  cv2.BORDER_CONSTANT,
                  value=border_color
              )
              frame = cv2.resize(frame, (self.width, self.height))

            # Apply edge detection
            if self.use_edge:
                edges = cv2.Canny(frame, self.edge_threshold1, self.edge_threshold2)
                edges_colored = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
                # Increase edge visibility
                frame = cv2.addWeighted(frame, 0.6, edges_colored, 0.4, 0)

            # Add overlay
            if self.use_overlay:
              # Add multiple overlay elements
              timestamp = f"Modified: {frame_number/self.fps:.1f}s"
              cv2.putText(
                  frame,
                  timestamp,
                  (10, 30),
                  cv2.FONT_HERSHEY_SIMPLEX,
                  1,
                  (255, 255, 255),
                  2
              )
              
              # Add additional overlay text
              effect_text = f"Zoom: {zoom_factor:.2f}x"
              cv2.putText(
                  frame,
                  effect_text,
                  (10, 70),
                  cv2.FONT_HERSHEY_SIMPLEX,
                  1,
                  (255, 255, 255),
                  2
              )

              # Add random geometric shapes as overlay
              if frame_number % 30 == 0:  # Every 30 frames
                  shape_color = (random.randint(0, 255), 
                              random.randint(0, 255), 
                              random.randint(0, 255))
                  cv2.rectangle(frame, 
                              (self.width-100, 10), 
                              (self.width-20, 90), 
                              shape_color, 
                              -1)

            out.write(frame)
            frame_number += 1

            # Update progress
            if self.progress_callback:
                progress = (frame_number / self.frame_count) * 100
                self.progress_callback(progress)

        self.cap.release()
        out.release()

    def generate_multiple_versions(self, num_versions=5):
        input_path = Path(self.input_path)
        output_dir = input_path.parent / "modified_versions"
        output_dir.mkdir(exist_ok=True)

        for i in range(num_versions):
            output_path = str(output_dir / f"modified_{datetime.now().strftime('%Y%m%d_%H%M%S')}{input_path.suffix}")
            if self.status_callback:
                self.status_callback(f"Generating version {i+1}...")
            
            # Reset video capture for each version
            self.cap = cv2.VideoCapture(self.input_path)
            
            # Generate modified version
            self.generate_modified_video(output_path)
            
        if self.status_callback:
            self.status_callback("All versions generated successfully!")

def main():
    root = tk.Tk()
    app = VideoGeneratorUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
