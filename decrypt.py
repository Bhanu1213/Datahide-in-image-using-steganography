import cv2
import numpy as np
import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

def bits_to_int(bits):
    return int("".join(map(str, bits)), 2)

def bits_to_str(bits):
    chars = [chr(bits_to_int(bits[i:i+8])) for i in range(0, len(bits), 8)]
    return "".join(chars)

def extract_data(image):
    flat = image.flatten()
    data_bits = [flat[i] & 1 for i in range(len(flat))]
    
    # Extract passcode length (first 16 bits)
    passcode_length = bits_to_int(data_bits[:16])
    data_bits = data_bits[16:]
    
    # Extract passcode
    passcode = bits_to_str(data_bits[:passcode_length * 8])
    data_bits = data_bits[passcode_length * 8:]
    
    # Extract secret message length (next 32 bits)
    message_length = bits_to_int(data_bits[:32])
    data_bits = data_bits[32:]
    
    # Extract secret message
    secret_message = bits_to_str(data_bits[:message_length * 8])
    
    return passcode, secret_message

def select_image():
    img_path = filedialog.askopenfilename(title="Select Encrypted Image", filetypes=[("PNG Image", "*.png")])
    if img_path:
        image_path_entry.delete(0, tk.END)
        image_path_entry.insert(0, img_path)

def decrypt():
    img_path = image_path_entry.get().strip()
    if not os.path.exists(img_path):
        messagebox.showerror("Error", "Encrypted image not found!")
        return
    
    image = cv2.imread(img_path)
    if image is None:
        messagebox.showerror("Error", "Failed to load the image.")
        return
    
    entered_passcode = passcode_entry.get()
    if not entered_passcode:
        messagebox.showerror("Error", "Passcode cannot be empty!")
        return
    
    try:
        extracted_passcode, secret_message = extract_data(image)
        if entered_passcode == extracted_passcode:
            messagebox.showinfo("Decryption Successful", f"Secret Message: {secret_message}")
        else:
            messagebox.showerror("Error", "Incorrect passcode!")
    except Exception as e:
        messagebox.showerror("Error", f"Decryption failed: {e}")

# GUI Setup
root = tk.Tk()
root.title("Steganography - Decrypt")
root.geometry("450x300")
style = ttk.Style(root)
style.theme_use('clam')

frame = ttk.Frame(root, padding="20")
frame.pack(expand=True)

# Image Path Input
ttk.Label(frame, text="Select Encrypted Image:").grid(row=0, column=0, sticky="w", pady=5)
image_path_entry = ttk.Entry(frame, width=40)
image_path_entry.grid(row=1, column=0, pady=5)
ttk.Button(frame, text="Browse", command=select_image).grid(row=1, column=1, padx=5)

# Passcode Input
ttk.Label(frame, text="Enter Passcode:").grid(row=2, column=0, sticky="w", pady=5)
passcode_entry = ttk.Entry(frame, width=40, show="*")
passcode_entry.grid(row=3, column=0, pady=5)

# Decrypt Button
decrypt_button = ttk.Button(frame, text="Decrypt", command=decrypt)
decrypt_button.grid(row=4, column=0, pady=20)

root.mainloop()