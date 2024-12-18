import threading
import os
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from PIL import Image, ImageTk, ImageDraw, ImageFont

class SnapScribe:
    def __init__(self, root):
        self.root = root
        self.root.title("SnapScribe - dodawanie stopki do zdjęć")
        self.image_folder = None
        self.images_list = []
        self.current_image_index = 0
        self.watermark_text = tk.StringVar()
        self.font_size = tk.IntVar(value=200)
        self.cancel_flag = False
        self.progress_window = None
        self.create_widgets()

    def create_widgets(self):
        ttk.Button(self.root, text="Wybierz folder ze zdjęciami", command=self.choose_folder).pack(pady=10)

        self.image_label = ttk.Label(self.root)
        self.image_label.pack(pady=10)

        ttk.Label(self.root, text="Wpisz tekst do dodania:").pack()
        self.text_entry = ttk.Entry(self.root, textvariable=self.watermark_text, width=50)
        self.text_entry.pack(padx = 10, pady=5)

        ttk.Label(self.root, text="Rozmiar czcionki:").pack()
        self.font_size_slider = ttk.Scale(self.root, from_=10, to=500, orient="horizontal", variable=self.font_size, command=self.update_preview)
        self.font_size_slider.pack(pady=5)

        ttk.Button(self.root, text="Odśwież podgląd", command=self.update_preview).pack(pady=10)

        frame = ttk.Frame(self.root)
        frame.pack()

        self.replace_label = ttk.Label(frame, text="Zastąp wszystkie zdjęcia:")
        self.replace_label.pack(side=tk.LEFT)

        self.replace_var = tk.IntVar()
        ttk.Checkbutton(frame, variable=self.replace_var).pack(side=tk.LEFT)

        self.apply_button = ttk.Button(self.root, text="Dodaj napis do wszystkich zdjęć", command=self.start_processing_thread)
        self.apply_button.pack(pady=10)

        self.info_label = ttk.Label(self.root, text="Wybierz folder, aby rozpocząć.")
        self.info_label.pack()

        self.author_label = ttk.Label(self.root, text="Autor: Michał Kirschniok")
        self.author_label.pack(pady=10)

    def choose_folder(self):
        folder = filedialog.askdirectory(title="Wybierz folder ze zdjęciami")
        if folder:
            self.image_folder = folder
            # Rekurencyjne zbieranie plików
            self.images_list = []
            for root, _, files in os.walk(folder):
                for file in files:
                    if file.lower().endswith(('png', 'jpg', 'jpeg', 'bmp')):
                        full_path = os.path.join(root, file)
                        self.images_list.append(full_path)
            
            if self.images_list:
                self.info_label.config(text=f"Znaleziono {len(self.images_list)} zdjęć.")
                self.load_image()
            else:
                messagebox.showerror("Błąd", "Wybrany folder nie zawiera zdjęć.")
        else:
            messagebox.showinfo("Info", "Nie wybrano folderu.")

    def load_image(self):
        if self.images_list:
            image_path = os.path.join(self.image_folder, self.images_list[self.current_image_index])
            self.original_image = Image.open(image_path)
            self.update_preview()

    def update_preview(self, event=None):
        if hasattr(self, 'original_image'):
            image = self.original_image.copy()
            draw = ImageDraw.Draw(image)

            font_size = self.font_size.get()
            try:
                font = ImageFont.truetype("arial.ttf", font_size)
            except:
                font = ImageFont.load_default()

            img_width, img_height = image.size
            text = self.watermark_text.get()
            text_width = draw.textlength(text, font=font)
            text_height = self.font_size.get()
            position = (img_width // 2 - text_width // 2, img_height - text_height - 20)

            overlay = Image.new("RGBA", image.size, (255, 255, 255, 0))
            overlay_draw = ImageDraw.Draw(overlay)
            overlay_draw.text(position, text, font=font, fill=(255, 255, 255, 150))
            image = Image.alpha_composite(image.convert("RGBA"), overlay)

            self.display_image(image)

    def display_image(self, image):
        image.thumbnail((500, 500))
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

        # Ustawienie modalności
        self.progress_window.transient(self.root)
        self.progress_window.grab_set()

        # Zablokowanie możliwości zmiany rozmiaru okna
        self.progress_window.resizable(False, False)

        self.center_window(self.progress_window, 400, 150)

        # Pasek postępu
        self.progress_label = ttk.Label(self.progress_window, text="Przetwarzanie zdjęć...")
        self.progress_label.pack(pady=10)
        self.progress_bar = ttk.Progressbar(self.progress_window, orient="horizontal", length=300, mode="determinate")
        self.progress_bar.pack(padx = 10, pady=10)
        self.progress_bar["maximum"] = len(self.images_list)

        # Przycisk Anuluj
        self.cancel_button = ttk.Button(self.progress_window, text="Anuluj", command=self.cancel_processing)
        self.cancel_button.pack(pady=10)


    
    def center_window(self, window, width, height):
        """Wyśrodkowuje okno na środku głównego okna."""
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
            return

        if not self.replace_var.get():
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
            if self.cancel_flag:  # Sprawdź, czy operacja została anulowana
                break

            # Aktualizacja etykiety w oknie paska postępu
            if self.progress_window and self.progress_window.winfo_exists():
                self.progress_label.config(text=f"Przetwarzanie zdjęć... {index + 1} z {len(self.images_list)}")
                self.progress_bar["value"] = index + 1
                self.progress_window.update_idletasks()
            else:
                # Okno paska postępu zostało zamknięte
                break

            # Relatywna ścieżka i przygotowanie folderów
            relative_path = os.path.relpath(image_path, self.image_folder)
            save_path = os.path.join(save_folder, relative_path)
            os.makedirs(os.path.dirname(save_path), exist_ok=True)

            # Otwieranie obrazu
            image = Image.open(image_path)
            draw = ImageDraw.Draw(image)

            # Czcionka i pozycja tekstu
            font_size = self.font_size.get()
            text = self.watermark_text.get()
            try:
                font = ImageFont.truetype("arial.ttf", font_size)
            except:
                font = ImageFont.load_default()

            img_width, img_height = image.size
            text_width = draw.textlength(text, font=font)
            text_height = font_size
            position = (img_width // 2 - text_width // 2, img_height - text_height - 20)

            # Dodanie znaku wodnego
            overlay = Image.new("RGBA", image.size, (255, 255, 255, 0))
            overlay_draw = ImageDraw.Draw(overlay)
            overlay_draw.text(position, text, font=font, fill=(255, 255, 255, 150))
            watermarked_image = Image.alpha_composite(image.convert("RGBA"), overlay)

            # Zapisanie obrazu
            watermarked_image.convert("RGB").save(save_path)

            if self.progress_window and self.progress_window.winfo_exists():
                self.progress_bar["value"] = index + 1
                self.progress_label.config(text=f"Przetwarzanie zdjęć... {index + 1} z {len(self.images_list)}")
                self.progress_window.update_idletasks()

        # Zamykanie okna postępu po zakończeniu
        if not self.cancel_flag:
            messagebox.showinfo("Sukces", f"Dodano napis do {len(self.images_list)} zdjęć.")
            self.info_label.config(text="Gotowe!")
        if self.progress_window:
            self.progress_window.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = SnapScribe(root)
    root.mainloop()