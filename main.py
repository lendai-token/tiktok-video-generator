import tkinter as tk
from tkinter import ttk, filedialog
import cv2
import numpy as np
from PIL import Image, ImageTk


class VideoComparisonTool:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Comparison Tool")
        self.root.geometry("1200x800")

        # Video paths
        self.video1_path = None
        self.video2_path = None

        self.setup_ui()

    def setup_ui(self):
        # Create main frames
        self.control_frame = ttk.Frame(self.root, padding="10")
        self.control_frame.pack(fill=tk.X)

        self.video_frame = ttk.Frame(self.root)
        self.video_frame.pack(fill=tk.BOTH, expand=True)

        # Video selection buttons
        ttk.Button(self.control_frame, text="Select Original Video",
                   command=lambda: self.select_video(1)).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.control_frame, text="Select Modified Video",
                   command=lambda: self.select_video(2)).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.control_frame, text="Compare Videos",
                   command=self.compare_videos).pack(side=tk.LEFT, padx=5)

        # Results display
        self.result_text = tk.Text(self.control_frame, height=20, width=50)
        self.result_text.pack(side=tk.RIGHT, padx=5)

        # Video preview labels
        self.video1_label = ttk.Label(self.video_frame)
        self.video1_label.grid(row=0, column=0, padx=5, pady=5)

        self.video2_label = ttk.Label(self.video_frame)
        self.video2_label.grid(row=0, column=1, padx=5, pady=5)

    def select_video(self, video_num):
        file_path = filedialog.askopenfilename(
            filetypes=[("Video files", "*.mp4 *.avi *.mov")]
        )
        if file_path:
            if video_num == 1:
                self.video1_path = file_path
                self.show_video_preview(file_path, self.video1_label)
            else:
                self.video2_path = file_path
                self.show_video_preview(file_path, self.video2_label)

    def show_video_preview(self, video_path, label):
        cap = cv2.VideoCapture(video_path)
        ret, frame = cap.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.resize(frame, (400, 300))
            photo = ImageTk.PhotoImage(image=Image.fromarray(frame))
            label.configure(image=photo)
            label.image = photo
        cap.release()

    def calculate_speed_difference(self, fps1, fps2):
        return abs(fps1 - fps2) / max(fps1, fps2) * 100

    def calculate_hsv_differences(self, frame1, frame2):
        hsv1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2HSV)
        hsv2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2HSV)

        # Calculate differences for each channel
        hue_diff = np.mean(np.abs(hsv1[:, :, 0] - hsv2[:, :, 0])) / 180 * 100
        sat_diff = np.mean(np.abs(hsv1[:, :, 1] - hsv2[:, :, 1])) / 255 * 100
        val_diff = np.mean(np.abs(hsv1[:, :, 2] - hsv2[:, :, 2])) / 255 * 100

        return hue_diff, sat_diff, val_diff

    def calculate_zoom_difference(self, frame1, frame2):
        # Calculate features and match them
        orb = cv2.ORB_create()
        kp1, des1 = orb.detectAndCompute(frame1, None)
        kp2, des2 = orb.detectAndCompute(frame2, None)

        if des1 is None or des2 is None or len(kp1) < 2 or len(kp2) < 2:
            return 0

        # Match features
        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        matches = bf.match(des1, des2)

        # Calculate average distance between matched points
        if len(matches) > 0:
            avg_dist = np.mean([m.distance for m in matches])
            # Normalize to percentage
            zoom_diff = min((avg_dist / 100) * 100, 100)
        else:
            zoom_diff = 0

        return zoom_diff

    def calculate_border_difference(self, frame1, frame2):
        h1, w1 = frame1.shape[:2]
        h2, w2 = frame2.shape[:2]

        # Define border regions (30 pixels from each edge)
        border_width = 30

        # Create masks for border regions
        def get_border_mask(frame):
            h, w = frame.shape[:2]
            mask = np.zeros_like(frame)
            # Fill border region with white
            mask[:border_width, :] = 255  # top
            mask[-border_width:, :] = 255  # bottom
            mask[:, :border_width] = 255  # left
            mask[:, -border_width:] = 255  # right
            return mask

        # Get border regions
        border_mask1 = get_border_mask(frame1)
        border_mask2 = get_border_mask(frame2)

        # Extract border regions
        border1 = cv2.bitwise_and(frame1, border_mask1)
        border2 = cv2.bitwise_and(frame2, border_mask2)

        # Calculate color difference in border regions
        diff = cv2.absdiff(border1, border2)
        border_diff = np.mean(diff) / 255 * 100

        # Calculate if borders exist (checking if there's a significant color change in border regions)
        border1_exists = np.mean(border1) > 10
        border2_exists = np.mean(border2) > 10

        # If one has border and other doesn't, increase difference
        if border1_exists != border2_exists:
            # High difference if one has border and other doesn't
            border_diff = max(border_diff, 80)

        return border_diff

    def analyze_videos(self):
        cap1 = cv2.VideoCapture(self.video1_path)
        cap2 = cv2.VideoCapture(self.video2_path)

        results = {
            'speed_diff': 0,
            'zoom_diff': 0,
            'hue_diff': 0,
            'saturation_diff': 0,
            'brightness_diff': 0,
            'border_diff': 0,
            'edge_diff': 0,
            'overlay_diff': 0
        }

        # Compare video properties
        fps1 = cap1.get(cv2.CAP_PROP_FPS)
        fps2 = cap2.get(cv2.CAP_PROP_FPS)
        results['speed_diff'] = self.calculate_speed_difference(fps1, fps2)

        # Sample frames for comparison
        frame_samples = 20
        all_differences = {key: [] for key in results.keys()}

        for _ in range(frame_samples):
            ret1, frame1 = cap1.read()
            ret2, frame2 = cap2.read()

            if not ret1 or not ret2:
                break

            # Resize frames to same size for comparison
            frame1 = cv2.resize(frame1, (640, 480))
            frame2 = cv2.resize(frame2, (640, 480))

            # Calculate zoom difference
            zoom_diff = self.calculate_zoom_difference(frame1, frame2)
            all_differences['zoom_diff'].append(zoom_diff)

            # Calculate HSV differences
            hue_diff, sat_diff, val_diff = self.calculate_hsv_differences(
                frame1, frame2)
            all_differences['hue_diff'].append(hue_diff)
            all_differences['saturation_diff'].append(sat_diff)
            all_differences['brightness_diff'].append(val_diff)

            # Border detection
            border_diff = self.calculate_border_difference(frame1, frame2)
            all_differences['border_diff'].append(border_diff)

            # Edge detection difference
            edge_diff = np.mean(cv2.absdiff(
                cv2.Canny(frame1, 100, 200),
                cv2.Canny(frame2, 100, 200)
            )) / 255 * 100
            all_differences['edge_diff'].append(edge_diff)

            # Overlay detection
            diff = cv2.absdiff(frame1, frame2)
            overlay_diff = np.mean(diff) / 255 * 100
            all_differences['overlay_diff'].append(overlay_diff)

        # Calculate average differences
        for key in all_differences:
            if all_differences[key]:
                results[key] = np.mean(all_differences[key])

        # Calculate overall difference with weighted components
        weights = {
            'speed_diff': 0.1,
            'zoom_diff': 0.1,
            'hue_diff': 0.15,
            'saturation_diff': 0.15,
            'brightness_diff': 0.15,
            'border_diff': 0.15,
            'edge_diff': 0.1,
            'overlay_diff': 0.1
        }

        overall_difference = sum(
            results[key] * weights[key] for key in weights)
        results['overall_difference'] = overall_difference
        results['overall_similarity'] = 100 - overall_difference

        cap1.release()
        cap2.release()

        return results

    def display_results(self, results):
        self.result_text.delete(1.0, tk.END)

        report = (
            f"=== Analysis Results ===\n\n"
            f"Overall Metrics:\n"
            f"• Similarity: {results['overall_similarity']:.2f}%\n"
            f"• Difference: {results['overall_difference']:.2f}%\n\n"
            f"Detailed Differences:\n"
            f"• Speed Difference: {results['speed_diff']:.2f}%\n"
            f"• Zoom Difference: {results['zoom_diff']:.2f}%\n"
            f"• Hue Difference: {results['hue_diff']:.2f}%\n"
            f"• Saturation Difference: {results['saturation_diff']:.2f}%\n"
            f"• Brightness Difference: {results['brightness_diff']:.2f}%\n"
            f"• Border Difference: {results['border_diff']:.2f}%\n"
            f"• Edge Difference: {results['edge_diff']:.2f}%\n"
            f"• Overlay Difference: {results['overlay_diff']:.2f}%\n"
        )

        self.result_text.insert(tk.END, report)
        self.result_text.insert(tk.END, "\n" + "="*40)

    def compare_videos(self):
        if not self.video1_path or not self.video2_path:
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, "Please select both videos first!")
            return

        results = self.analyze_videos()
        self.display_results(results)


if __name__ == "__main__":
    root = tk.Tk()
    app = VideoComparisonTool(root)
    root.mainloop()
