from pathlib import Path
from tkinter import Tk, messagebox
import customtkinter as ctk
from services.social import Social
from gui.app import Aplicacion

def main():
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")
    try:
        social = Social(Path(__file__).resolve().parent)
    except (OSError, ValueError, TypeError, KeyError) as error:
        raiz = Tk()
        raiz.withdraw()
        messagebox.showerror("Social UNA · Datos", str(error), parent=raiz)
        raiz.destroy()
        return
    Aplicacion(social).mainloop()

if __name__ == "__main__":
    main()
