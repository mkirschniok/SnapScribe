import threading
import sys
import os
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from PIL import Image, ImageTk, ImageDraw, ImageFont

class SnapScribe:
    def __init__(self, root):
        self.root = root
        self.root.title("SnapScribe - dodawanie stopki do zdjęć")
        path = self.resource_path("icon.ico")
        self.root.iconbitmap(path)
        self.image_folder = None
        self.images_list = []
        self.current_image_index = 0
        self.cancel_flag = False
        self.progress_window = None
        self.create_widgets()
        self.root.resizable(False, False)

    def resource_path(self, relative_path):
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        preview_frame = ttk.Frame(main_frame)
        preview_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        path = self.resource_path("placeholder.png")
        placeholder_image = Image.open(path).resize((400, 300))
        self.tk_image = ImageTk.PhotoImage(placeholder_image)
        self.image_label = ttk.Label(preview_frame, image=self.tk_image, compound="center", anchor="center")
        self.image_label.pack(fill=tk.BOTH, expand=True)
        self.image_label.bind("<Button-1>", lambda event: self.choose_folder())
        ttk.Separator(main_frame, orient="vertical").grid(row=0, column=1, sticky="ns", padx=10)
        options_frame = ttk.Frame(main_frame)
        options_frame.grid(row=0, column=1, sticky="nsew")
        self.folder_button = ttk.Button(options_frame, text="Otwórz folder ze zdjęciami")
        self.folder_button.grid(row=0, column=0, pady=(0, 10), sticky="ew")
        self.folder_button.config(command=self.choose_folder)
        self.folder_label = ttk.Label(options_frame, text="Wybrany folder: (brak)", anchor="center", compound="center")
        self.folder_label.grid(row=0, column=1, pady=(0, 10), sticky="ew")

        ttk.Label(options_frame, text="Wpisz tekst do dodania:").grid(row=1, column=0, columnspan=2, sticky="w")
        self.text_entry = ttk.Entry(options_frame, width=30)
        self.text_entry.insert(0, "Twój tekst")
        self.text_entry.grid(row=1, column=1, pady=5, sticky="ew")

        ttk.Label(options_frame, text="Rozmiar czcionki:").grid(row=2, column=0, sticky="w")
        vcmd = (self.root.register(self.validate_font_size), "%P")
        self.font_size_entry = ttk.Entry(options_frame, width=30, validate="key", validatecommand=vcmd)
        self.font_size_entry.insert(0, "200")
        self.font_size_entry.grid(row=2, column=1, pady=5, sticky="ew")


        self.update_preview_button = ttk.Button(options_frame, text="Aktualizuj podgląd")
        self.update_preview_button.grid(row=3, column=0, columnspan=2, pady=(10, 10), sticky="ew")
        self.update_preview_button.config(command=self.update_preview)

        self.create_copy_var = tk.BooleanVar(value=True)
        ttk.Radiobutton(options_frame, text="Utwórz kopię zdjęć", variable=self.create_copy_var, value=True).grid(row=4, column=0, sticky="w")
        ttk.Radiobutton(options_frame, text="Zastąp wszystkie zdjęcia", variable=self.create_copy_var, value=False).grid(row=4, column=1, sticky="w")

        self.process_button = ttk.Button(options_frame, text="Dodaj napis do wszystkich zdjęć")
        self.process_button.grid(row=5, column=0, columnspan=2, pady=(10, 10), sticky="ew")
        self.process_button.config(command=self.start_processing_thread)

        self.info_label = ttk.Label(options_frame, text="Znaleziono 0 zdjęć.", anchor="center")
        self.info_label.grid(row=6, column=0, columnspan=2, pady=(0, 10), sticky="ew")

        self.author_label = ttk.Label(options_frame, text="Autor: Michał Kirschniok\nWersja 0.5", anchor="center", compound="center", justify="center")
        self.author_label.grid(row=7, column=0, columnspan=2, pady=(10, 0), sticky="ew")

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)
        options_frame.rowconfigure(0, weight=1)
        options_frame.rowconfigure(1, weight=1)
        options_frame.rowconfigure(2, weight=1)
        options_frame.rowconfigure(3, weight=1)
        options_frame.rowconfigure(4, weight=1)
        options_frame.rowconfigure(5, weight=1)
        options_frame.rowconfigure(6, weight=1)
        options_frame.rowconfigure(7, weight=1)


    def validate_font_size(self, value_if_allowed):
        if value_if_allowed == "" or (value_if_allowed.isdigit() and int(value_if_allowed) <= 1000):
            return True
        return False

    def choose_folder(self):
        folder = filedialog.askdirectory(title="Wybierz folder ze zdjęciami")
        if folder:
            self.image_folder = folder
            self.images_list = []
            for root, _, files in os.walk(folder):
                for file in files:
                    if file.lower().endswith(('png', 'jpg', 'jpeg', 'bmp')):
                        full_path = os.path.join(root, file)
                        self.images_list.append(full_path)
            
            if self.images_list:
                self.info_label.config(text=f"Znaleziono {len(self.images_list)} zdjęć.")
                self.load_image()
                self.folder_label.config(text=f"Wybrany folder: {os.path.basename(folder)}")
                self.image_label.unbind("<Button-1>")
            else:
                messagebox.showerror("Błąd", "Wybrany folder nie zawiera zdjęć.")
        else:
            messagebox.showinfo("Info", "Nie wybrano folderu.")

    def load_image(self):
        if self.images_list:
            image_path = os.path.join(self.image_folder, self.images_list[self.current_image_index])
            try:
                self.original_image = Image.open(image_path)
            except:
                messagebox.showerror("Błąd", f"Nie można otworzyć pliku: {image_path}")
                return
            self.update_preview()

    def update_preview(self, event=None):
        if hasattr(self, 'original_image'):
            image = self.original_image.copy()
            draw = ImageDraw.Draw(image)
            font_size = int(self.font_size_entry.get())
            try:
                font = ImageFont.truetype("arial.ttf", font_size)
            except:
                font = ImageFont.load_default()
            img_width, img_height = image.size
            text = self.text_entry.get()
            text_width = draw.textlength(text, font=font)
            text_height = font_size
            position = (img_width // 2 - text_width // 2, img_height - text_height - 20)

            overlay = Image.new("RGBA", image.size, (255, 255, 255, 0))
            overlay_draw = ImageDraw.Draw(overlay)
            overlay_draw.text(position, text, font=font, fill=(255, 255, 255, 150))
            image = Image.alpha_composite(image.convert("RGBA"), overlay)
            image.thumbnail((400, 300))
            self.tk_image = ImageTk.PhotoImage(image)
            self.image_label.config(image=self.tk_image)
        
    def start_processing_thread(self):
        self.cancel_flag = False
        self.create_progress_window()
        processing_thread = threading.Thread(target=self.apply_watermark)
        processing_thread.start()

    def create_progress_window(self):
        self.progress_window = tk.Toplevel(self.root)
        self.progress_window.title("Postęp przetwarzania")

        self.progress_window.transient(self.root)
        self.progress_window.grab_set()

        self.progress_window.resizable(False, False)
        self.center_window(self.progress_window, 400, 150)

        self.progress_label = ttk.Label(self.progress_window, text="Przetwarzanie zdjęć...")
        self.progress_label.pack(pady=10)
        self.progress_bar = ttk.Progressbar(self.progress_window, orient="horizontal", length=300, mode="determinate")
        self.progress_bar.pack(padx = 10, pady=10)
        self.progress_bar["maximum"] = len(self.images_list)

        self.cancel_button = ttk.Button(self.progress_window, text="Anuluj", command=self.cancel_processing)
        self.cancel_button.pack(pady=10)


    
    def center_window(self, window, width, height):
        root_x = self.root.winfo_x()
        root_y = self.root.winfo_y()
        root_width = self.root.winfo_width()
        root_height = self.root.winfo_height()
        x = root_x + (root_width // 2) - (width // 2)
        y = root_y + (root_height // 2) - (height // 2)
        window.geometry(f"{width}x{height}+{x}+{y}")


    def cancel_processing(self):
        self.cancel_flag = True
        if self.progress_window and self.progress_window.winfo_exists():
            self.progress_window.destroy()
            self.progress_window = None
        self.info_label.config(text="Anulowano przetwarzanie.")
        messagebox.showinfo("Info", "Anulowano przetwarzanie.")

    def apply_watermark(self):
        if not self.images_list:
            messagebox.showerror("Błąd", "Brak zdjęć do przetworzenia.")
            if self.progress_window:
                self.progress_window.destroy()
            return
        if not self.text_entry.get():
            messagebox.showerror("Błąd", "Wpisz tekst do dodania.")
            if self.progress_window:
                self.progress_window.destroy()
            return
        if not self.font_size_entry.get():
            messagebox.showerror("Błąd", "Podaj rozmiar czcionki.")
            if self.progress_window:
                self.progress_window.destroy()
            return

        if self.create_copy_var.get():
            save_folder = filedialog.askdirectory(title="Wybierz folder do zapisu zdjęć")
            if not save_folder:
                messagebox.showinfo("Info", "Nie wybrano folderu do zapisu.")
                if self.progress_window:
                    self.progress_window.destroy()
                return
        else:
            save_folder = self.image_folder

        self.info_label.config(text="Przetwarzanie...")

        for index, image_path in enumerate(self.images_list):
            if self.cancel_flag:
                break

            if self.progress_window and self.progress_window.winfo_exists():
                self.progress_label.config(text=f"Przetwarzanie zdjęć... {index + 1} z {len(self.images_list)}")
                self.progress_bar["value"] = index + 1
                self.progress_window.update_idletasks()
            else:
                break

            relative_path = os.path.relpath(image_path, self.image_folder)
            save_path = os.path.join(save_folder, relative_path)
            os.makedirs(os.path.dirname(save_path), exist_ok=True)

            try:
                image = Image.open(image_path)
            except:
                messagebox.showerror("Błąd", f"Nie można otworzyć pliku: {image_path}")
                self.info_label.config(text="Błąd!")
                self.cancel_flag = True
                if self.progress_window:
                    self.progress_window.destroy()
                return
            draw = ImageDraw.Draw(image)

            font_size = int(self.font_size_entry.get())
            text = self.text_entry.get()
            try:
                font = ImageFont.truetype("arial.ttf", font_size)
            except:
                font = ImageFont.load_default()

            img_width, img_height = image.size
            text_width = draw.textlength(text, font=font)
            text_height = font_size
            position = (img_width // 2 - text_width // 2, img_height - text_height - 20)

            overlay = Image.new("RGBA", image.size, (255, 255, 255, 0))
            overlay_draw = ImageDraw.Draw(overlay)
            overlay_draw.text(position, text, font=font, fill=(255, 255, 255, 150))
            watermarked_image = Image.alpha_composite(image.convert("RGBA"), overlay)

            watermarked_image.convert("RGB").save(save_path)

            if self.progress_window and self.progress_window.winfo_exists():
                self.progress_bar["value"] = index + 1
                self.progress_label.config(text=f"Przetwarzanie zdjęć... {index + 1} z {len(self.images_list)}")
                self.progress_window.update_idletasks()

        if not self.cancel_flag:
            messagebox.showinfo("Sukces", f"Dodano napis do {len(self.images_list)} zdjęć.")
            self.info_label.config(text="Gotowe!")
        if self.progress_window:
            self.progress_window.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = SnapScribe(root)
    root.mainloop()