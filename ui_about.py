import customtkinter as ctk
from PIL import Image
import os

class AboutWindow(ctk.CTkFrame):
    def __init__(self, parent, main_app):
        super().__init__(parent, fg_color="#FFF0F5")
        self.main_app = main_app
        # --- ไม่ต้องมี self.assets ถ้าใช้ main_app.load_image ---
        self.setup_ui()
    
    def on_show(self):
        # หน้านี้เนื้อหาไม่เปลี่ยน ไม่ต้องทำอะไร
        pass
    
    def setup_ui(self):
        # กำหนดให้แถวที่ 1 (main_frame) ขยายตามแนวตั้ง
        self.grid_rowconfigure(1, weight=1) 
        # กำหนดให้คอลัมน์ที่ 0 (คอลัมน์เดียว) ขยายตามแนวนอน
        self.grid_columnconfigure(0, weight=1) 
        
        # --- 1. สร้างส่วนหัว (Header) ---
        header = ctk.CTkFrame(
            self, # ใส่ header ลงใน AboutWindow (self)
            fg_color="#FFFFFF",
            corner_radius=0,
            height=70,
            border_width=1,
            border_color="#FFEBEE"
        )
        # .grid() ใช้วาง widget ลงในแถว/คอลัมน์ที่กำหนด
        # row=0 คือแถวบนสุด, column=0 คือคอลัมน์แรก
        # sticky="ew" คือให้ยืดเต็มความกว้าง (East-West)
        header.grid(row=0, column=0, sticky="ew", pady=(0, 20)) 
        # กำหนดให้คอลัมน์ที่ 1 ใน header ขยายได้ (เพื่อให้ปุ่มไปอยู่ขวาสุด)
        header.grid_columnconfigure(1, weight=1) 
        
        # ใส่ Label "เกี่ยวกับเรา"
        label_title = ctk.CTkLabel(
            header, # ใส่ label ลงใน header
            text="ℹ️ เกี่ยวกับเรา",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#FFB6C1"
        )
        # .pack() ใช้วาง widget ต่อๆ กัน (ง่ายกว่า grid ในกรณีเรียงๆ กัน)
        # side="left" คือให้อยู่ชิดซ้าย
        label_title.pack(side="left", padx=30, pady=20) 
        
        # ใส่ปุ่ม "กลับหน้าหลัก"
        back_button = ctk.CTkButton(
            header, # ใส่ปุ่มลงใน header
            text="🏠 กลับหน้าหลัก",
            fg_color="transparent",
            text_color="#FFB6C1",
            hover_color="#FFE4E1",
            font=ctk.CTkFont(size=14),
            # command คือฟังก์ชันที่จะทำงานเมื่อกดปุ่ม
            # lambda: คือการสร้างฟังก์ชันเล็กๆ ชั่วคราว
            command=lambda: self.main_app.navigate_to('HomeWindow') 
        )
        # side="right" คือให้อยู่ชิดขวา
        back_button.pack(side="right", padx=30, pady=20) 

        # --- 2. สร้างส่วนเนื้อหาหลัก (ที่เลื่อนได้) ---
        main_frame = ctk.CTkScrollableFrame(
            self, # ใส่ main_frame ลงใน AboutWindow (self)
            fg_color="transparent",
            scrollbar_button_color="#FFB6C1"
        )
        # วาง main_frame ลงในแถวที่ 1 (ใต้ header)
        # sticky="nsew" คือให้ยืดเต็มพื้นที่ทั้ง 4 ทิศ (North-South-East-West)
        main_frame.grid(row=1, column=0, sticky="nsew", padx=30, pady=20) 
        
        # --- 3. สร้างการ์ดสีขาวสำหรับใส่เนื้อหาทั้งหมด ---
        content_card = ctk.CTkFrame(
            main_frame, # ใส่การ์ดลงใน main_frame (ที่เลื่อนได้)
            fg_color="#FFFFFF",
            corner_radius=20,
            border_width=2,
            border_color="#FFEBEE"
        )
        # fill="both" คือให้ขยายเต็มพื้นที่ตาม parent (main_frame)
        # expand=True คืออนุญาตให้ขยายได้
        content_card.pack(fill="both", expand=True, padx=50, pady=20) 

        # --- 4. ใส่เนื้อหาลงในการ์ด (ส่วนของร้าน) ---
        shop_section = ctk.CTkFrame(content_card, fg_color="#FFE4E1", corner_radius=15)
        shop_section.pack(fill="x", padx=30, pady=(30, 20)) # fill="x" คือยืดเต็มความกว้าง
        
        shop_icon = ctk.CTkLabel(shop_section, text="🎀", font=ctk.CTkFont(size=60))
        shop_icon.pack(pady=(20, 10))
        shop_name = ctk.CTkLabel(shop_section, text="Dollie Shop", font=ctk.CTkFont(size=36, weight="bold"), text_color="#FF6B9D")
        shop_name.pack()
        shop_subtitle = ctk.CTkLabel(shop_section, text="ระบบจัดการร้านขายตุ๊กตาออนไลน์", font=ctk.CTkFont(size=16), text_color="#6D4C41")
        shop_subtitle.pack(pady=(5, 20))
        
        # --- 5. ใส่เนื้อหาลงในการ์ด (ส่วนคำอธิบาย) ---
        desc_frame = ctk.CTkFrame(content_card, fg_color="transparent")
        desc_frame.pack(fill="x", padx=40, pady=20)
        
        description_label = ctk.CTkLabel(
            desc_frame,
            text="ระบบจัดการร้านค้าออนไลน์สำหรับขายตุ๊กตาและของเล่น\n"
                 "พัฒนาด้วย Python และ CustomTkinter\n"
                 "มีระบบจัดการสินค้า ตะกร้าสินค้า การชำระเงิน และระบบ Admin ที่ครบครัน",
            font=ctk.CTkFont(size=14),
            text_color="#6D4C41",
            justify="center" # จัดข้อความให้อยู่กึ่งกลาง (ถ้ามีหลายบรรทัด)
        )
        description_label.pack(pady=10)
        
        # --- 6. เส้นคั่น ---
        separator1 = ctk.CTkFrame(content_card, height=2, fg_color="#FFEBEE")
        separator1.pack(fill="x", padx=40, pady=20)
        
        # --- 7. ใส่เนื้อหาลงในการ์ด (ส่วนหัวผู้พัฒนา) ---
        dev_header = ctk.CTkFrame(content_card, fg_color="#FFE4E1", corner_radius=15)
        dev_header.pack(fill="x", padx=30, pady=20)
        
        dev_title = ctk.CTkLabel(dev_header, text="👩‍💻 ผู้พัฒนาโปรแกรม", font=ctk.CTkFont(size=24, weight="bold"), text_color="#6D4C41")
        dev_title.pack(pady=15)
        
        # --- 8. ใส่เนื้อหาลงในการ์ด (ส่วนโปรไฟล์ผู้พัฒนา) ---
        profile_frame = ctk.CTkFrame(content_card, fg_color="#FFF0F5", corner_radius=15)
        profile_frame.pack(fill="x", padx=40, pady=20)
        
        # --- 8.1 โหลดและแสดงรูปภาพผู้พัฒนา ---
        try:
            image_path = "assets/developer.jpg" # กำหนด path รูปตรงๆ
            
            # เช็คว่าไฟล์รูปมีอยู่จริงไหม
            if os.path.exists(image_path):
                # ใช้ PIL เปิดรูป
                pil_image = Image.open(image_path)
                # ปรับขนาดรูป
                pil_image_resized = pil_image.resize((300, 300), Image.Resampling.LANCZOS)
                # แปลงเป็น CTkImage
                ctk_dev_image = ctk.CTkImage(pil_image_resized, size=(300, 300))
                # สร้าง Label เพื่อแสดงรูป (text ว่างเปล่า)
                dev_image_label = ctk.CTkLabel(profile_frame, text="", image=ctk_dev_image)
                dev_image_label.pack(pady=(20, 10))
            else:
                # ถ้าไม่มีไฟล์รูป ก็แสดง Emoji แทน
                dev_emoji_label = ctk.CTkLabel(profile_frame, text="👩‍💻", font=ctk.CTkFont(size=80))
                dev_emoji_label.pack(pady=(20, 10))
                
        except Exception as e: # ดักจับ error ทุกชนิด
            print(f"เกิด Error ตอนโหลดรูปผู้พัฒนา: {e}")
            # ถ้ามี error ก็แสดง Emoji แทน
            dev_emoji_label_error = ctk.CTkLabel(profile_frame, text="👩‍💻", font=ctk.CTkFont(size=80))
            dev_emoji_label_error.pack(pady=(20, 10))
            
        # --- 8.2 แสดงข้อมูลผู้พัฒนา ---
        info_container = ctk.CTkFrame(profile_frame, fg_color="transparent")
        info_container.pack(pady=20, padx=30)
        
        dev_name = ctk.CTkLabel(info_container, text="นางสาว พิมลวรรณ มาตะราช", font=ctk.CTkFont(size=22, weight="bold"), text_color="#FF6B9D")
        dev_name.pack(pady=5)
        dev_faculty = ctk.CTkLabel(info_container, text="คณะศึกษาศาสตร์ สาขาคอมพิวเตอร์ศึกษา มหาวิทยาลัยขอนแก่น", font=ctk.CTkFont(size=14), text_color="#6D4C41")
        dev_faculty.pack(pady=5)

        id_frame = ctk.CTkFrame(info_container, fg_color="#FFFFFF", corner_radius=10)
        id_frame.pack(pady=10)
        dev_id = ctk.CTkLabel(id_frame, text="🎓 รหัสนักศึกษา: 673050139-2", font=ctk.CTkFont(size=16), text_color="#6D4C41")
        dev_id.pack(padx=20, pady=10)
        
        # --- 9. ใส่เนื้อหาลงในการ์ด (ส่วนข้อมูลติดต่อ) ---
        contact_frame = ctk.CTkFrame(content_card, fg_color="transparent")
        contact_frame.pack(fill="x", padx=40, pady=20)
        
        contact_title = ctk.CTkLabel(contact_frame, text="📞 ติดต่อสอบถาม", font=ctk.CTkFont(size=18, weight="bold"), text_color="#6D4C41")
        contact_title.pack(pady=10)
        
        phone_frame = ctk.CTkFrame(contact_frame, fg_color="#FFFFFF", corner_radius=10, border_width=1, border_color="#FFEBEE")
        phone_frame.pack(pady=5)
        phone_label = ctk.CTkLabel(phone_frame, text="📱 เบอร์โทรศัพท์: 086-379-7202", font=ctk.CTkFont(size=15), text_color="#6D4C41")
        phone_label.pack(padx=30, pady=12)
        
        fb_frame = ctk.CTkFrame(contact_frame, fg_color="#FFFFFF", corner_radius=10, border_width=1, border_color="#FFEBEE")
        fb_frame.pack(pady=5)
        fb_label = ctk.CTkLabel(fb_frame, text="📘 Facebook: Phimonwan Martarach", font=ctk.CTkFont(size=15), text_color="#6D4C41")
        fb_label.pack(padx=30, pady=12)
        
        # --- 10. ใส่เนื้อหาลงในการ์ด (ส่วน Footer) ---
        footer_frame = ctk.CTkFrame(content_card, fg_color="transparent")
        footer_frame.pack(fill="x", padx=40, pady=(20, 30))
        
        footer_text1 = ctk.CTkLabel(footer_frame, text="💖 พัฒนาด้วยความตั้งใจ", font=ctk.CTkFont(size=16, weight="bold"), text_color="#FFB6C1")
        footer_text1.pack()
        footer_text2 = ctk.CTkLabel(footer_frame, text="© 2025 Dollie Shop. All rights reserved.", font=ctk.CTkFont(size=12), text_color="gray50")
        footer_text2.pack(pady=(5, 0))