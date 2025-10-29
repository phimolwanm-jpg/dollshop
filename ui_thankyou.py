# M:/doll_shop/ui_thankyou.py (ปรับสไตล์ให้ง่าย)

import customtkinter as ctk

class ThankYouWindow(ctk.CTkFrame):
    def __init__(self, parent, main_app):
        """
        Constructor ของหน้า ThankYouWindow
        """
        super().__init__(parent, fg_color="#F8F9FA") # ตั้งสีพื้นหลัง frame หลัก
        self.main_app = main_app
        # --- ไม่ต้องมี self.assets ถ้าใช้ main_app.load_image ---
        # self.assets = main_app.assets 
        self.order_id_received = None # เปลี่ยนชื่อตัวแปรให้ชัดเจน

        # ไม่ต้องสร้าง UI ทันที รอ on_show เรียก
        # self.setup_ui() 

    def on_show(self, order_id=None):
        """
        ทำงานทุกครั้งที่เปิดหน้านี้: รับ order_id, ลบ UI เก่า, สร้าง UI ใหม่
        """
        # 1. เก็บ order_id ที่ได้รับมา
        self.order_id_received = order_id 
        
        # 2. ลบ widget เก่าทั้งหมดทิ้ง (ถ้ามี)
        for widget in self.winfo_children():
            widget.destroy()
            
        # 3. สร้าง UI ใหม่ทั้งหมด
        self.setup_ui() 

    def setup_ui(self):
        """สร้างองค์ประกอบ UI ทั้งหมดของหน้า Thank You"""
        
        # --- 1. กำหนดการขยายตัวของ Grid หลัก ---
        # (ไม่จำเป็นต้อง pack_propagate(False) ถ้าใช้ grid layout ถูกต้อง)
        # self.pack_propagate(False) 
        # ให้คอลัมน์ 0 (คอลัมน์เดียว) ขยายเต็มความกว้าง
        self.grid_columnconfigure(0, weight=1) 
        # ให้แถวที่ 0 (แถวเดียว) ขยายเต็มความสูง (เพื่อให้ main_frame อยู่กลางจอ)
        self.grid_rowconfigure(0, weight=1)    

        # --- 2. สร้าง Frame หลักสำหรับวางเนื้อหาตรงกลาง ---
        main_content_frame = ctk.CTkFrame(self, # ใส่ใน ThankYouWindow (self)
                                          fg_color="transparent") # พื้นหลังโปร่งใส
        # ใช้ grid วาง frame นี้ตรงกลาง (row=0, column=0 คือช่องเดียวที่มี)
        main_content_frame.grid(row=0, column=0) 

        # --- 3. โหลดและแสดงรูปภาพตุ๊กตา ---
        # (สมมติว่า main.py มี load_image แล้ว)
        thank_you_doll_image = self.main_app.load_image("thank_you_doll.png", size=(250, 250)) 
        image_label = ctk.CTkLabel(main_content_frame, # ใส่ใน frame หลัก
                                   text="", # ไม่มีข้อความ
                                   image=thank_you_doll_image)
        # วางรูปภาพ (เว้นระยะล่าง 20)
        image_label.pack(pady=(0, 20)) 
        
        # --- 4. แสดงข้อความขอบคุณ ---
        thank_you_text_label = ctk.CTkLabel(main_content_frame, 
                                            text="ขอบคุณที่อุดหนุนนะคะ!", 
                                            font=ctk.CTkFont(size=32, weight="bold"), 
                                            text_color="#FF69B4") # สีชมพูเข้ม
        thank_you_text_label.pack(pady=10) # เว้นระยะบนล่าง 10
        
        # --- 5. แสดงหมายเลข Order ID (ถ้ามี) ---
        # เตรียมข้อความ
        if self.order_id_received: # เช็คว่าได้รับ order_id มาหรือไม่
            order_confirmation_text = f"คำสั่งซื้อของคุณหมายเลข #{self.order_id_received} ได้รับการยืนยันแล้ว"
        else: # ถ้าไม่ได้รับ (กรณีผิดพลาด)
            order_confirmation_text = "คำสั่งซื้อของคุณได้รับการยืนยันแล้ว"
            
        # สร้าง Label แสดงข้อความ
        order_info_label = ctk.CTkLabel(main_content_frame, 
                                        text=order_confirmation_text, 
                                        font=ctk.CTkFont(size=16), 
                                        text_color="gray") # สีเทา
        order_info_label.pack() # วางต่อท้ายข้อความขอบคุณ

        # --- 6. สร้าง Frame สำหรับวางปุ่ม ---
        buttons_frame = ctk.CTkFrame(main_content_frame, fg_color="transparent")
        # วาง frame นี้ใต้ label แสดง order_id (เว้นระยะบน 30)
        buttons_frame.pack(pady=30) 
        
        # --- 6.1 ปุ่ม "กลับไปหน้าหลัก" ---
        go_home_button = ctk.CTkButton(buttons_frame, # ใส่ใน frame ปุ่ม
                                       text="กลับไปหน้าหลัก", 
                                       height=40, corner_radius=20,
                                       # command: เมื่อกด ให้เรียก main_app.navigate_to เพื่อไปหน้า 'HomeWindow'
                                       command=lambda: self.main_app.navigate_to('HomeWindow')) 
        # วางปุ่มชิดซ้าย (เว้นระยะข้าง 10)
        go_home_button.pack(side="left", padx=10) 
        
        # --- 6.2 ปุ่ม "ดูประวัติการสั่งซื้อ" ---
        view_history_button = ctk.CTkButton(buttons_frame, # ใส่ใน frame ปุ่ม
                                           text="ดูประวัติการสั่งซื้อ", 
                                           height=40, corner_radius=20, 
                                           fg_color="transparent", # ปุ่มโปร่งใส
                                           border_width=1, # มีเส้นขอบ
                                           # command: เมื่อกด ให้เรียก main_app.navigate_to เพื่อไปหน้า 'OrderHistoryWindow'
                                           command=lambda: self.main_app.navigate_to('OrderHistoryWindow')) 
        # วางปุ่มชิดซ้าย (ต่อจากปุ่ม home)
        view_history_button.pack(side="left", padx=10) 
        # --- จบการสร้าง UI ---