import tkinter as tk
from tkinter import ttk, messagebox
import random
import string
import qrcode
from PIL import Image, ImageTk
import os

class WiFiCardGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("مولد كروت الواي فاي الاحترافي")
        self.root.geometry("850x650") # Increased size slightly for better layout
        # self.root.resizable(False, False) # Allow resizing for now, can be set back

        # إنشاء مجلد لحفظ الصور إذا لم يكن موجوداً
        self.cards_folder = "wifi_cards"
        if not os.path.exists(self.cards_folder):
            os.makedirs(self.cards_folder)

        self.generated_cards_data = [] # To store (ssid, password, encryption) tuples

        # إعداد واجهة المستخدم
        self.setup_ui()

    def setup_ui(self):
        # إطار العنوان
        title_frame = tk.Frame(self.root, bg="#2c3e50")
        title_frame.pack(fill=tk.X, pady=(0,10)) # Added some bottom padding

        title_label = tk.Label(title_frame, text="مولد كروت الواي فاي الاحترافي", font=("Arial", 22, "bold"),
                              fg="white", bg="#2c3e50")
        title_label.pack(pady=15) # Adjusted padding

        # --- Main Content Area (Input + Results/QR) ---
        main_content_frame = tk.Frame(self.root, padx=10, pady=10)
        main_content_frame.pack(fill=tk.BOTH, expand=True)

        # إطار الإدخال (Left Side)
        input_outer_frame = tk.Frame(main_content_frame)
        input_outer_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0,10))

        input_frame = tk.LabelFrame(input_outer_frame, text="إعدادات الكرت", font=("Arial", 12, "bold"), padx=15, pady=15)
        input_frame.pack(fill=tk.X)

        # اسم الشبكة (SSID)
        tk.Label(input_frame, text="اسم الشبكة (SSID):", font=("Arial", 11)).grid(row=0, column=0, sticky="w", pady=5)
        self.ssid_entry = tk.Entry(input_frame, font=("Arial", 11), width=30)
        self.ssid_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        self.ssid_entry.insert(0, "MyNetwork") # Default value

        # كلمة المرور
        tk.Label(input_frame, text="كلمة المرور:", font=("Arial", 11)).grid(row=1, column=0, sticky="w", pady=5)
        self.password_entry = tk.Entry(input_frame, font=("Arial", 11), width=30)
        self.password_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        self.password_entry.insert(0, "random") # Default value

        # نوع التشفير
        tk.Label(input_frame, text="نوع التشفير:", font=("Arial", 11)).grid(row=2, column=0, sticky="w", pady=5)
        self.encryption_var = tk.StringVar(value="WPA2")
        encryption_options = ["WPA2", "WPA", "WEP", "None"]
        self.encryption_menu = ttk.Combobox(input_frame, textvariable=self.encryption_var,
                                           values=encryption_options, font=("Arial", 11), width=28, state="readonly")
        self.encryption_menu.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

        # عدد الكروت المطلوبة
        tk.Label(input_frame, text="عدد الكروت:", font=("Arial", 11)).grid(row=3, column=0, sticky="w", pady=5)
        self.count_var = tk.IntVar(value=1)
        self.count_spinbox = tk.Spinbox(input_frame, from_=1, to=100, textvariable=self.count_var,
                                       font=("Arial", 11), width=5)
        self.count_spinbox.grid(row=3, column=1, sticky="w", padx=10, pady=5)

        input_frame.grid_columnconfigure(1, weight=1) # Make entry widgets expand

        # أزرار التحكم
        button_frame = tk.Frame(input_outer_frame, pady=20)
        button_frame.pack(fill=tk.X)

        self.generate_btn = tk.Button(button_frame, text="توليد الكروت", font=("Arial", 12, "bold"),
                               bg="#3498db", fg="white", command=self.generate_cards, width=12, height=1)
        self.generate_btn.pack(side=tk.LEFT, padx=(0,10), expand=True, fill=tk.X)

        self.save_btn = tk.Button(button_frame, text="حفظ الكروت", font=("Arial", 12, "bold"),
                           bg="#2ecc71", fg="white", command=self.save_cards, width=12, height=1, state=tk.DISABLED)
        self.save_btn.pack(side=tk.LEFT, expand=True, fill=tk.X)

        # --- Results Area (List + QR on Right Side) ---
        results_area_frame = tk.Frame(main_content_frame)
        results_area_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # إطار عرض النتائج (Listbox)
        result_list_frame = tk.LabelFrame(results_area_frame, text="الكروت المولدة", font=("Arial", 12, "bold"), padx=10, pady=10)
        result_list_frame.pack(fill=tk.BOTH, expand=True, pady=(0,10))

        scrollbar = tk.Scrollbar(result_list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.result_list = tk.Listbox(result_list_frame, font=("Arial", 11), yscrollcommand=scrollbar.set,
                                    selectmode=tk.SINGLE, height=10)
        self.result_list.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.result_list.yview)
        self.result_list.bind("<<ListboxSelect>>", self.on_card_select)

        # إطار QR Code
        qr_display_frame = tk.LabelFrame(results_area_frame, text="رمز QR", font=("Arial", 12, "bold"), padx=10, pady=10)
        qr_display_frame.pack(fill=tk.X, pady=(5,0)) # Fills X, fixed height

        self.qr_label = tk.Label(qr_display_frame, bg="white") # Added bg for clarity
        self.qr_label.pack(pady=5) # Centered in its frame
        self.clear_qr_code_display() # Show placeholder initially


    def generate_cards(self):
        ssid = self.ssid_entry.get().strip()
        password_input = self.password_entry.get().strip()
        encryption = self.encryption_var.get()
        count = self.count_var.get()

        if not ssid:
            messagebox.showerror("خطأ الإدخال", "الرجاء إدخال اسم الشبكة (SSID)")
            return

        if encryption != "None" and not password_input :
            messagebox.showerror("خطأ الإدخال", "الرجاء إدخال كلمة المرور أو اكتب 'random'")
            return
        
        # Handle "None" encryption case where password should be empty
        if encryption == "None":
            password_input = "" # Force empty password for "None" type encryption

        self.result_list.delete(0, tk.END)
        self.generated_cards_data = []
        self.clear_qr_code_display()

        for i in range(count):
            current_password = password_input
            if password_input.lower() == "random" and encryption != "None":
                length = 12
                chars = string.ascii_letters + string.digits # Simplified for typical Wi-Fi
                # For stronger passwords: string.ascii_letters + string.digits + "!@#$%^&*"
                current_password = ''.join(random.choice(chars) for _ in range(length))
            elif encryption == "None":
                current_password = "" # Ensure password is blank for 'None'

            self.generated_cards_data.append({
                "ssid": ssid,
                "password": current_password,
                "encryption": encryption,
                "id": i + 1
            })
            self.result_list.insert(tk.END, f"كارت واي فاي #{i+1} - {ssid}")

        if self.generated_cards_data:
            self.result_list.select_set(0) # Select the first item
            self.on_card_select(None) # Trigger QR display for the first item
            self.save_btn.config(state=tk.NORMAL)
        else:
            self.save_btn.config(state=tk.DISABLED)

    def on_card_select(self, event): # event can be None if called programmatically
        selection = self.result_list.curselection()
        if selection:
            index = selection[0]
            if 0 <= index < len(self.generated_cards_data):
                card_data = self.generated_cards_data[index]
                self.show_qr_code(card_data)
        else:
            self.clear_qr_code_display()

    def _create_wifi_qr_string(self, ssid, password, encryption):
        # Ensure encryption type is one of WPA, WPA2, WEP, or nopass (for None)
        # The standard uses 'WPA' for WPA/WPA2, 'WEP' for WEP, and 'nopass' for open networks.
        # However, some readers are more flexible.
        # Let's stick to common practice.
        enc_type = encryption.upper()
        if enc_type == "NONE":
            enc_type = "nopass" # Common for QR
            password = "" # Explicitly clear password for 'nopass'
        elif enc_type not in ["WPA", "WPA2", "WEP"]:
             enc_type = "WPA" # Default to WPA if unknown

        return f"WIFI:T:{enc_type};S:{ssid};P:{password};;"

    def show_qr_code(self, card_data):
        wifi_qr_string = self._create_wifi_qr_string(
            card_data["ssid"], card_data["password"], card_data["encryption"]
        )

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=8, # Adjusted for the display area
            border=2,
        )
        qr.add_data(wifi_qr_string)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        # Fixed size for QR display area, e.g., 200x200
        # Let's try to fit it in a 240x240 area
        display_size = 220
        img = img.resize((display_size, display_size), Image.LANCZOS)

        photo = ImageTk.PhotoImage(img)
        self.qr_label.config(image=photo, width=display_size, height=display_size)
        self.qr_label.image = photo # Keep a reference!

    def clear_qr_code_display(self):
        # Create a small blank image or a placeholder text/image
        try:
            # Attempt to create a placeholder image
            placeholder_img = Image.new('RGB', (220, 220), color = (240, 240, 240)) # Light gray
            # You could draw text on it too:
            # from PIL import ImageDraw
            # draw = ImageDraw.Draw(placeholder_img)
            # draw.text((10, 100), "حدد كارت لعرض QR", fill=(100,100,100))
            photo = ImageTk.PhotoImage(placeholder_img)
            self.qr_label.config(image=photo, text="")
            self.qr_label.image = photo
        except Exception as e:
            # Fallback if PIL fails for placeholder (e.g., minimal install)
            self.qr_label.config(image=None, text="لا يوجد QR لعرضه", width=30, height=10)
            print(f"Error creating placeholder: {e}")


    def save_cards(self):
        if not self.generated_cards_data:
            messagebox.showerror("خطأ الحفظ", "لا توجد كروت لحفظها. قم بتوليد الكروت أولاً.")
            return

        saved_count = 0
        try:
            for card_data in self.generated_cards_data:
                card_id = card_data["id"]
                ssid = card_data["ssid"]
                password = card_data["password"]
                encryption = card_data["encryption"]

                # Sanitize SSID for filename (replace invalid characters)
                safe_ssid_name = "".join(c if c.isalnum() else "_" for c in ssid)
                base_filename = f"{self.cards_folder}/wifi_{safe_ssid_name}_card_{card_id}"

                # حفظ البيانات النصية
                text_content = f"SSID: {ssid}\n"
                if encryption != "None": # Only include password if not an open network
                    text_content += f"Password: {password}\n"
                text_content += f"Encryption: {encryption}\n"
                text_content += f"----------------------------------\n"
                text_content += f"Connect using QR code or manually.\n"


                with open(f"{base_filename}.txt", "w", encoding="utf-8") as f:
                    f.write(text_content)

                # حفظ QR Code
                wifi_qr_string = self._create_wifi_qr_string(ssid, password, encryption)
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_M, # Medium for better scan
                    box_size=10,
                    border=4,
                )
                qr.add_data(wifi_qr_string)
                qr.make(fit=True)
                img = qr.make_image(fill_color="black", back_color="white")
                img.save(f"{base_filename}.png")
                saved_count +=1

            messagebox.showinfo("نجاح الحفظ",
                                f"تم حفظ {saved_count} كارت واي فاي بنجاح في مجلد '{self.cards_folder}'")
        except Exception as e:
            messagebox.showerror("خطأ أثناء الحفظ", f"حدث خطأ: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    # Add a theme for a more modern look (optional)
    try:
        style = ttk.Style(root)
        # Available themes: 'winnative', 'clam', 'alt', 'default', 'classic', 'vista', 'xpnative'
        # 'clam' or 'alt' often look good. 'vista' or 'winnative' on Windows.
        if os.name == 'nt': # Windows
             style.theme_use('vista')
        else:
             style.theme_use('clam') # A common cross-platform theme
    except Exception:
        print("ttk themes not available or failed to apply.")
        pass # Continue without theme if it fails

    app = WiFiCardGenerator(root)
    root.mainloop()