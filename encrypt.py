import cv2
import os
import numpy as np
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

def int_to_bits(num, bit_length):
    return [int(b) for b in format(num, f'0{bit_length}b')]

def str_to_bits(s):
    bits = []
    for char in s:
        bits.extend([int(b) for b in format(ord(char), '08b')])
    return bits

def embed_data(image, data_bits):
    height, width, channels = image.shape
    total_pixels = height * width * channels

    if len(data_bits) > total_pixels:
        raise ValueError("Data too large to embed in this image!")

    bit_index = 0
    for row in range(height):
        for col in range(width):
            for channel in range(channels):
                if bit_index < len(data_bits):
                    pixel_value = image[row, col, channel]
                    pixel_value = pixel_value & 0xFE  # Clear the LSB
                    pixel_value |= data_bits[bit_index]  # Set the LSB to the data bit
                    image[row, col, channel] = np.clip(pixel_value, 0, 255)
                    bit_index += 1
                else:
                    return image

    return image

def select_image():
    img_path = filedialog.askopenfilename(title="Select Image", filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
    if img_path:
        image_path_entry.delete(0, tk.END)
        image_path_entry.insert(0, img_path)

def select_output():
    output_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG Image", "*.png")])
    if output_path:
        output_path_entry.delete(0, tk.END)
        output_path_entry.insert(0, output_path)

def encrypt():
    img_path = image_path_entry.get().strip()
    if not os.path.exists(img_path):
        messagebox.showerror("Error", "Input image not found!")
        return
    image = cv2.imread(img_path)
    if image is None:
        messagebox.showerror("Error", "Failed to load the image. Please check the file format.")
        return

    secret_message = secret_message_entry.get()
    passcode = passcode_entry.get()
    if not secret_message or not passcode:
        messagebox.showerror("Error", "Secret message and passcode cannot be empty!")
        return

    header_bits = []
    header_bits.extend(int_to_bits(len(passcode), 16))
    header_bits.extend(str_to_bits(passcode))
    header_bits.extend(int_to_bits(len(secret_message), 32))
    header_bits.extend(str_to_bits(secret_message))

    try:
        encoded_image = embed_data(image, header_bits)
    except ValueError as e:
        messagebox.showerror("Error", str(e))
        return

    output_path = output_path_entry.get().strip()
    if not output_path:
        messagebox.showerror("Error", "Please select an output file.")
        return
    
    cv2.imwrite(output_path, encoded_image)
    messagebox.showinfo("Success", f"Encryption complete! Saved as '{output_path}'.")

root = tk.Tk()
root.title("Steganography - Encrypt")
root.geometry("450x400")
style = ttk.Style(root)
style.theme_use('clam')

frame = ttk.Frame(root, padding="20")
frame.pack(expand=True)

# Image Path Input
ttk.Label(frame, text="Select Input Image:").grid(row=0, column=0, sticky="w", pady=5)
image_path_entry = ttk.Entry(frame, width=40)
image_path_entry.grid(row=1, column=0, pady=5)
ttk.Button(frame, text="Browse", command=select_image).grid(row=1, column=1, padx=5)

# Secret Message Input
ttk.Label(frame, text="Enter Secret Message:").grid(row=2, column=0, sticky="w", pady=5)
secret_message_entry = ttk.Entry(frame, width=40)
secret_message_entry.grid(row=3, column=0, pady=5)

# Passcode Input
ttk.Label(frame, text="Enter Passcode:").grid(row=4, column=0, sticky="w", pady=5)
passcode_entry = ttk.Entry(frame, width=40, show="*")
passcode_entry.grid(row=5, column=0, pady=5)

# Output Path Input
ttk.Label(frame, text="Select Output Image Path:").grid(row=6, column=0, sticky="w", pady=5)
output_path_entry = ttk.Entry(frame, width=40)
output_path_entry.grid(row=7, column=0, pady=5)
ttk.Button(frame, text="Browse", command=select_output).grid(row=7, column=1, padx=5)

# Encrypt Button
encrypt_button = ttk.Button(frame, text="Encrypt", command=encrypt)
encrypt_button.grid(row=8, column=0, pady=20)

root.mainloop()
