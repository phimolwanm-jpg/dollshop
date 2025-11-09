import customtkinter as ctk

class ThankYouWindow(ctk.CTkFrame):
    def __init__(self, parent, main_app):
        super().__init__(parent, fg_color="#F8F9FA")
        self.main_app = main_app
        self.order_id = None
    
    def on_show(self, order_id=None):
        """เปิดหน้านี้ - รับหมายเลขคำสั่งซื้อ"""
        # เก็บหมายเลข
        self.order_id = order_id
        
        # ลบของเก่า
        for widget in self.winfo_children():
            widget.destroy()
        
        # สร้างหน้าจอใหม่
        self.create_ui()
    
    def create_ui(self):
        """สร้างหน้าจอขอบคุณ"""
        # ตั้งค่าให้อยู่กลางจอ
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # กรอบหลักตรงกลาง
        center_box = ctk.CTkFrame(self, fg_color="transparent")
        center_box.grid(row=0, column=0)
        
        # รูปตุ๊กตา
        self.show_doll_image(center_box)
        
        # ข้อความขอบคุณ
        self.show_thank_message(center_box)
        
        # หมายเลขคำสั่งซื้อ
        self.show_order_number(center_box)
        
        # ปุ่มต่างๆ
        self.create_buttons(center_box)
    
    def show_doll_image(self, parent):
        """แสดงรูปตุ๊กตา"""
        img = self.main_app.load_image("thank_you_doll.png", size=(250, 250))
        img_label = ctk.CTkLabel(parent, text="", image=img)
        img_label.pack(pady=(0, 20))
    
    def show_thank_message(self, parent):
        """แสดงข้อความขอบคุณ"""
        msg = ctk.CTkLabel(parent,
                          text="ขอบคุณที่อุดหนุนนะคะ!",
                          font=ctk.CTkFont(size=32, weight="bold"),
                          text_color="#FF69B4")
        msg.pack(pady=10)
    
    def show_order_number(self, parent):
        """แสดงหมายเลขคำสั่งซื้อ"""
        # เตรียมข้อความ
        if self.order_id:
            text = f"คำสั่งซื้อของคุณหมายเลข #{self.order_id} ได้รับการยืนยันแล้ว"
        else:
            text = "คำสั่งซื้อของคุณได้รับการยืนยันแล้ว"
        
        # แสดงข้อความ
        order_label = ctk.CTkLabel(parent,
                                   text=text,
                                   font=ctk.CTkFont(size=16),
                                   text_color="gray")
        order_label.pack()
    
    def create_buttons(self, parent):
        """สร้างปุ่มควบคุม"""
        # กรอบปุ่ม
        btn_box = ctk.CTkFrame(parent, fg_color="transparent")
        btn_box.pack(pady=30)
        
        # ปุ่มกลับหน้าหลัก
        home_btn = ctk.CTkButton(btn_box,
                                text="กลับไปหน้าหลัก",
                                height=40,
                                corner_radius=20,
                                command=self.go_home)
        home_btn.pack(side="left", padx=10)
        
        # ปุ่มดูประวัติ
        history_btn = ctk.CTkButton(btn_box,
                                    text="ดูประวัติการสั่งซื้อ",
                                    height=40,
                                    corner_radius=20,
                                    fg_color="transparent",
                                    border_width=1,
                                    command=self.go_history)
        history_btn.pack(side="left", padx=10)
    
    def go_home(self):
        """กลับหน้าหลัก"""
        self.main_app.navigate_to('HomeWindow')
    
    def go_history(self):
        """ไปหน้าประวัติ"""
        self.main_app.navigate_to('OrderHistoryWindow')