import tkinter as tk
import tkinter.font as font
from Gesture_Controller import gest_control
from eye import eye_move
from samvk import vk_keyboard
from PIL import Image, ImageTk
from Proton import proton_chat
import customtkinter as ctk

window = tk.Tk()
window.title("Gesture Controlled Virtual Mouse and Keyboard")
window.iconphoto(False, tk.PhotoImage(file='mn.png'))
window.geometry('1080x700')

# Luxury dark background
window.configure(bg='#D1D0D0')
frame1 = tk.Frame(window, bg='#D1D0D0')


label_title = tk.Label(
    frame1,
    text="< VisionX >",
    fg="#5C4E4E",  # Luxurious gold
    bg="#D1D0D0"  # Clean white background
)
label_font = font.Font(
    family="Segoe UI",  
    size=40,
    weight="bold",
)
label_title['font'] = label_font
label_title.grid(row=0, column=0, columnspan=4, pady=(30, 25), sticky="ew")
frame1.grid_columnconfigure(0, weight=1)
frame1.grid_columnconfigure(1, weight=1)
frame1.grid_columnconfigure(2, weight=1)
frame1.grid_columnconfigure(3, weight=1)


icon = Image.open('icons/man.jpeg').convert("RGBA")
icon = icon.resize((220, 180), Image.Resampling.LANCZOS)

# Create a transparent background matching the interface
bg = Image.new("RGBA", icon.size, (255, 255, 227, 0))  # Transparent background
bg.paste(icon, (0, 0), icon)  # Use icon's alpha channel as mask

icon_tk = ImageTk.PhotoImage(bg)

label_icon = tk.Label(frame1, image=icon_tk, bg='#D1D0D0')
label_icon.grid(row=1, pady=(10, 10), column=2, sticky="n")


# Convert button images to CTkImage format

btn1_img = Image.open('icons/bot.png')
btn1_image = ctk.CTkImage(light_image=btn1_img, dark_image=btn1_img, size=(40, 40))

btn2_img = Image.open('icons/keyboard.png')
btn2_image = ctk.CTkImage(light_image=btn2_img, dark_image=btn2_img, size=(40, 40))

btn3_img = Image.open('icons/eye.jpeg')
btn3_image = ctk.CTkImage(light_image=btn3_img, dark_image=btn3_img, size=(40, 40))

btn4_img = Image.open('icons/hand.png')
btn4_image = ctk.CTkImage(light_image=btn4_img, dark_image=btn4_img, size=(40, 40))

btn5_img = Image.open('icons/exit.png')
btn5_image = ctk.CTkImage(light_image=btn5_img, dark_image=btn5_img, size=(30, 30))


# --------------- Buttons -------------------#

# Set appearance mode and color theme
#ctk.set_appearance_mode("dark")
#ctk.set_default_color_theme("blue")

# Premium luxury buttons with individual accent colors
btn1 = ctk.CTkButton(frame1, text='', height=75, width=150, 
                     fg_color='#988686', hover_color='#5C4E4E',  # Purple glow
                     corner_radius=10, cursor='hand2',
                     command=proton_chat, image=btn1_image)
btn1.grid(row=3, pady=(20, 10), padx=(10, 20))

btn2 = ctk.CTkButton(frame1, text='', height=75, width=150,
                     fg_color='#988686', hover_color='#5C4E4E',  # Blue glow
                     corner_radius=10, cursor='hand2',
                     command=vk_keyboard, image=btn2_image)
btn2.grid(row=3, pady=(20, 10), column=3, padx=(20, 10))

btn3 = ctk.CTkButton(frame1, text='', height=75, width=150,
                     fg_color='#988686', hover_color='#5C4E4E',  # Cyan glow
                     corner_radius=10, cursor='hand2',
                     command=eye_move, image=btn3_image)
btn3.grid(row=5, pady=(20, 10), padx=(10, 20))

btn4 = ctk.CTkButton(frame1, text='', height=75, width=150,
                     fg_color='#988686', hover_color='#5C4E4E',  # Rose glow
                     corner_radius=10, cursor='hand2',
                     command=gest_control, image=btn4_image)
btn4.grid(row=5, pady=(20, 10), column=3, padx=(20, 10))

btn5 = ctk.CTkButton(frame1, text='', height=75, width=150,
                     fg_color='#988686', hover_color='#5C4E4E',  # Red glow for exit
                     corner_radius=10, cursor='hand2',
                     command=window.quit, image=btn5_image)
btn5.grid(row=6, pady=(20, 10), column=2)

frame1.pack()
window.mainloop()