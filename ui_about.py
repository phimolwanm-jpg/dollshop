import customtkinter as ctk

class AboutWindow(ctk.CTkFrame):
    def __init__(self, parent, main_app):
        super().__init__(parent, fg_color="#FFF0F5")
        self.main_app = main_app
        self.setup_ui()
    
    def on_show(self):
        """(ฟังก์ชันนี้ถูกเรียกทุกครั้งที่เปิดหน้านี้)"""
        pass # หน้านี้เป็นข้อมูลนิ่ง ไม่ต้องทำอะไร
    
    # --- 1. "ผู้จัดการ" UI ---
    
    def setup_ui(self):
        """
        ฟังก์ชันหลักสำหรับสร้าง UI
        ทำหน้าที่เป็น "ผู้จัดการ" เรียกฟังก์ชันย่อยมาทำงาน
        """
        self.grid_rowconfigure(1, weight=1) 
        self.grid_columnconfigure(0, weight=1) 
        
        # สร้างส่วนประกอบหลัก
        self.create_header()
        self.create_content_area()

    # --- 2. "ผู้ช่วย" สร้างส่วนประกอบ (Helper Functions) ---

    def create_header(self):
        """สร้างแถบ Header ด้านบน (มี τίtle และปุ่มกลับ)"""
        header = ctk.CTkFrame(
            self,
            fg_color="#FFFFFF",
            corner_radius=0,
            height=70,
            border_width=1,
            border_color="#FFEBEE"
        )
        header.grid(row=0, column=0, sticky="ew", pady=(0, 20)) 
        header.grid_columnconfigure(1, weight=1) 
        
        label_title = ctk.CTkLabel(
            header,
            text="ℹ️ เกี่ยวกับเรา",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#FFB6C1"
        )
        label_title.pack(side="left", padx=30, pady=20) 
        
        # เปลี่ยน lambda เป็นฟังก์ชันที่มีชื่อ
        back_button = ctk.CTkButton(
            header,
            text="🏠 กลับหน้าหลัก",
            fg_color="transparent",
            text_color="#FFB6C1",
            hover_color="#FFE4E1",
            font=ctk.CTkFont(size=14),
            command=self.navigate_home # <-- ชัดเจนขึ้น
        )
        back_button.pack(side="right", padx=30, pady=20) 

    def create_content_area(self):
        """สร้างพื้นที่ Scrollable และการ์ดสีขาวสำหรับใส่เนื้อหา"""
        main_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            scrollbar_button_color="#FFB6C1"
        )
        main_frame.grid(row=1, column=0, sticky="nsew", padx=30, pady=20) 
        
        content_card = ctk.CTkFrame(
            main_frame,
            fg_color="#FFFFFF",
            corner_radius=20,
            border_width=2,
            border_color="#FFEBEE"
        )
        content_card.pack(fill="both", expand=True, padx=50, pady=20) 

        # --- เรียก "ผู้ช่วยย่อย" มาเติมเนื้อหาในการ์ด ---
        self.create_shop_section(content_card)
        self.create_description_section(content_card)
        self.create_separator(content_card)
        self.create_developer_section(content_card)
        self.create_contact_section(content_card)
        self.create_footer_section(content_card)

    def create_shop_section(self, parent):
        """สร้างส่วนข้อมูลร้าน 'Dollie Shop'"""
        shop_section = ctk.CTkFrame(parent, fg_color="#FFE4E1", corner_radius=15)
        shop_section.pack(fill="x", padx=30, pady=(30, 20))
        
        ctk.CTkLabel(shop_section, text="🎀", font=ctk.CTkFont(size=60)).pack(pady=(20, 10))
        ctk.CTkLabel(shop_section, text="Dollie Shop", font=ctk.CTkFont(size=36, weight="bold"), text_color="#FF6B9D").pack()
        ctk.CTkLabel(shop_section, text="ระบบจัดการร้านขายตุ๊กตาออนไลน์", font=ctk.CTkFont(size=16), text_color="#6D4C41").pack(pady=(5, 20))
        
    def create_description_section(self, parent):
        """สร้างส่วนคำอธิบายโปรเจกต์"""
        desc_frame = ctk.CTkFrame(parent, fg_color="transparent")
        desc_frame.pack(fill="x", padx=40, pady=20)
        
        description_text = (
            "ระบบจัดการร้านค้าออนไลน์สำหรับขายตุ๊กตาและของเล่น\n"
            "พัฒนาด้วย Python และ CustomTkinter\n"
            "มีระบบจัดการสินค้า ตะกร้าสินค้า การชำระเงิน และระบบ Admin ที่ครบครัน"
        )
        
        ctk.CTkLabel(
            desc_frame,
            text=description_text,
            font=ctk.CTkFont(size=14),
            text_color="#6D4C41",
            justify="center"
        ).pack(pady=10)
        
    def create_separator(self, parent):
        """สร้างเส้นคั่น"""
        separator = ctk.CTkFrame(parent, height=2, fg_color="#FFEBEE")
        separator.pack(fill="x", padx=40, pady=20)
        
    def create_developer_section(self, parent):
        """สร้างส่วนข้อมูลผู้พัฒนา (หัวข้อ, รูป, ชื่อ)"""
        
        # --- 7. หัวข้อผู้พัฒนา ---
        dev_header = ctk.CTkFrame(parent, fg_color="#FFE4E1", corner_radius=15)
        dev_header.pack(fill="x", padx=30, pady=20)
        ctk.CTkLabel(dev_header, text="👩‍💻 ผู้พัฒนาโปรแกรม", font=ctk.CTkFont(size=24, weight="bold"), text_color="#6D4C41").pack(pady=15)
        
        # --- 8. โปรไฟล์ผู้พัฒนา ---
        profile_frame = ctk.CTkFrame(parent, fg_color="#FFF0F5", corner_radius=15)
        profile_frame.pack(fill="x", padx=40, pady=20)
        
        # --- ใช้ฟังก์ชันจาก main_app ---
        # สะอาดและสั้นกว่าเดิมมาก!
        # ไม่ต้องใช้ try...except หรือ os.path.exists
        # เพราะ self.main_app.load_image() จัดการให้หมดแล้ว
        # (ถ้า "developer.jpg" ไม่มี มันจะโหลด "default_profile.png" ให้แทน)
        dev_image = self.main_app.load_image("developer.jpg", size=(300, 300))
        dev_image_label = ctk.CTkLabel(profile_frame, text="", image=dev_image)
        dev_image_label.pack(pady=(20, 10))
            
        # --- ข้อมูลผู้พัฒนา ---
        info_container = ctk.CTkFrame(profile_frame, fg_color="transparent")
        info_container.pack(pady=20, padx=30)
        
        ctk.CTkLabel(info_container, text="นางสาว พิมลวรรณ มาตะราช", font=ctk.CTkFont(size=22, weight="bold"), text_color="#FF6B9D").pack(pady=5)
        ctk.CTkLabel(info_container, text="คณะศึกษาศาสตร์ สาขาคอมพิวเตอร์ศึกษา มหาวิทยาลัยขอนแก่น", font=ctk.CTkFont(size=14), text_color="#6D4C41").pack(pady=5)

        id_frame = ctk.CTkFrame(info_container, fg_color="#FFFFFF", corner_radius=10)
        id_frame.pack(pady=10)
        ctk.CTkLabel(id_frame, text="🎓 รหัสนักศึกษา: 673050139-2", font=ctk.CTkFont(size=16), text_color="#6D4C41").pack(padx=20, pady=10)
        
    def create_contact_section(self, parent):
        """สร้างส่วนข้อมูลติดต่อ (เบอร์, FB)"""
        contact_frame = ctk.CTkFrame(parent, fg_color="transparent")
        contact_frame.pack(fill="x", padx=40, pady=20)
        
        ctk.CTkLabel(contact_frame, text="📞 ติดต่อสอบถาม", font=ctk.CTkFont(size=18, weight="bold"), text_color="#6D4C41").pack(pady=10)
        
        phone_frame = ctk.CTkFrame(contact_frame, fg_color="#FFFFFF", corner_radius=10, border_width=1, border_color="#FFEBEE")
        phone_frame.pack(pady=5)
        ctk.CTkLabel(phone_frame, text="📱 เบอร์โทรศัพท์: 086-379-7202", font=ctk.CTkFont(size=15), text_color="#6D4C41").pack(padx=30, pady=12)
        
        fb_frame = ctk.CTkFrame(contact_frame, fg_color="#FFFFFF", corner_radius=10, border_width=1, border_color="#FFEBEE")
        fb_frame.pack(pady=5)
        ctk.CTkLabel(fb_frame, text="📘 Facebook: Phimonwan Martarach", font=ctk.CTkFont(size=15), text_color="#6D4C41").pack(padx=30, pady=12)
        
    def create_footer_section(self, parent):
        """สร้างส่วน Footer ล่างสุด"""
        footer_frame = ctk.CTkFrame(parent, fg_color="transparent")
        footer_frame.pack(fill="x", padx=40, pady=(20, 30))
        
        ctk.CTkLabel(footer_frame, text="💖 พัฒนาด้วยความตั้งใจ", font=ctk.CTkFont(size=16, weight="bold"), text_color="#FFB6C1").pack()
        ctk.CTkLabel(footer_frame, text="© 2025 Dollie Shop. All rights reserved.", font=ctk.CTkFont(size=12), text_color="gray50").pack(pady=(5, 0))

    # --- 3. ฟังก์ชันสำหรับการกระทำ (Actions) ---

    def navigate_home(self):
        """
        ฟังก์ชันสำหรับปุ่ม 'กลับหน้าหลัก'
        (ถูกเรียกโดย 'command=self.navigate_home')
        """
        self.main_app.navigate_to('HomeWindow')