import cv2
import numpy as np
import customtkinter as ctk
from threading import Thread
from PIL import Image
from tkinter import filedialog, messagebox


class CameraApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Live Camera with Filters and Brightness Control")
        self.root.geometry("1200x600")
        self.root.resizable(False, False)
        
        # Set theme for CustomTkinter
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")

        # Camera initialization
        self.capture = cv2.VideoCapture(0)
        self.running = True
        self.current_filter = "Normal"
        self.brightness_value = 1.0  # Default brightness (no change)

        # Left frame for controls
        self.control_frame = ctk.CTkFrame(self.root, width=400, height=600)
        self.control_frame.pack(side="left", fill="y")

        # Add widgets to control frame
        self.filter_label = ctk.CTkLabel(self.control_frame, text="Select Filter:", font=("Arial", 16))
        self.filter_label.pack(pady=20)

        self.filter_var = ctk.StringVar(value="Normal")
        self.filter_dropdown = ctk.CTkOptionMenu(
            self.control_frame, 
            values=["Normal", "Grayscale", "Sepia", "Edge Detection", "Invert", "Blur", "Sharpen", "Emboss", "HSV"],
            command=self.set_filter
        )
        self.filter_dropdown.pack(pady=10)

        self.brightness_label = ctk.CTkLabel(self.control_frame, text="Adjust Brightness:", font=("Arial", 16))
        self.brightness_label.pack(pady=20)

        self.brightness_scale = ctk.CTkSlider(
            self.control_frame,
            from_=0.5,
            to=2.0,
            number_of_steps=150,
            command=self.set_brightness
        )
        self.brightness_scale.set(1.0)  # Default brightness
        self.brightness_scale.pack(pady=10)

        self.save_button = ctk.CTkButton(self.control_frame, text="Save Image", command=self.save_image)
        self.save_button.pack(pady=20)

        self.exit_button = ctk.CTkButton(self.control_frame, text="Exit", command=self.exit_app)
        self.exit_button.pack(pady=10)

        # Right frame for live camera
        self.camera_frame = ctk.CTkFrame(self.root, width=800, height=600)
        self.camera_frame.pack(side="right", fill="both", expand=True)

        self.video_label = ctk.CTkLabel(self.camera_frame, text="")
        self.video_label.pack(padx=10, pady=10, anchor="center")

        # Start the video stream thread
        self.thread = Thread(target=self.update_frame, daemon=True)
        self.thread.start()

    def set_filter(self, filter_name):
        self.current_filter = filter_name

    def set_brightness(self, value):
        self.brightness_value = float(value)

    def apply_filter(self, frame):
        if self.current_filter == "Grayscale":
            return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        elif self.current_filter == "Sepia":
            kernel = np.array([[0.272, 0.534, 0.131],
                               [0.349, 0.686, 0.168],
                               [0.393, 0.769, 0.189]])
            return cv2.transform(frame, kernel)
        elif self.current_filter == "Edge Detection":
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            return cv2.Canny(gray, 50, 150)
        elif self.current_filter == "Invert":
            return cv2.bitwise_not(frame)
        elif self.current_filter == "Blur":
            return cv2.GaussianBlur(frame, (15, 15), 0)
        elif self.current_filter == "Sharpen":
            kernel = np.array([[0, -1, 0],
                               [-1, 5, -1],
                               [0, -1, 0]])
            return cv2.filter2D(frame, -1, kernel)
        elif self.current_filter == "Emboss":
            kernel = np.array([[-2, -1, 0],
                               [-1, 1, 1],
                               [0, 1, 2]])
            return cv2.filter2D(frame, -1, kernel)
        elif self.current_filter == "HSV":
            return cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        return frame  # Normal

    def adjust_brightness(self, frame):
        """
        Adjust the brightness of the frame by multiplying pixel values with the brightness value.
        """
        frame = cv2.convertScaleAbs(frame, alpha=self.brightness_value, beta=0)
        return frame

    def update_frame(self):
        while self.running:
            ret, frame = self.capture.read()
            if not ret:
                break

            # Apply brightness adjustment
            frame = self.adjust_brightness(frame)

            # Apply the selected filter
            filtered_frame = self.apply_filter(frame)

            # Resize the frame to 800x600
            filtered_frame = cv2.resize(filtered_frame, (800, 600))

            # Convert to RGB for Tkinter
            if self.current_filter in ["Grayscale", "Edge Detection", "HSV"]:
                if self.current_filter == "HSV":
                    filtered_frame = cv2.cvtColor(filtered_frame, cv2.COLOR_HSV2RGB)
            else:
                filtered_frame = cv2.cvtColor(filtered_frame, cv2.COLOR_BGR2RGB)

            # Store the last filtered frame for saving
            self.last_frame = filtered_frame

            # Convert to PIL Image
            img = Image.fromarray(filtered_frame)

            # Convert to CTkImage
            ctk_image = ctk.CTkImage(light_image=img, dark_image=img, size=(800, 600))

            # Update the video label
            self.video_label.configure(image=ctk_image)
            self.video_label.image = ctk_image

        self.capture.release()

    def save_image(self):
        if hasattr(self, "last_frame"):
            # Open a native OS file dialog to select save location
            file_path = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")]
            )
            if file_path:
                # Save the frame
                save_frame = cv2.cvtColor(self.last_frame, cv2.COLOR_RGB2BGR)
                cv2.imwrite(file_path, save_frame)

                # Display a success message
                messagebox.showinfo("Image Saved", f"Image saved successfully at:\n{file_path}")

    def exit_app(self):
        self.running = False
        self.root.quit()


# Main application
if __name__ == "__main__":
    root = ctk.CTk()
    app = CameraApp(root)
    root.mainloop()
