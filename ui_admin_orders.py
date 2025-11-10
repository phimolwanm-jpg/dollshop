import customtkinter as ctk
from tkinter import ttk, messagebox
import os
from PIL import Image, ImageTk

class AdminOrdersWindow(ctk.CTkFrame):
    def __init__(self, parent, main_app):
        super().__init__(parent, fg_color="#FFF0F5")
        self.main_app = main_app
        self.db = main_app.db
        
        # ประกาศตัวแปรของคลาส
        self.tree = None
        self.slip_win = None # สำหรับเก็บหน้าต่างสลิป
        
        # ### <<< เพิ่มใหม่ >>> ###
        # ตัวแปรสำหรับเก็บปุ่มที่ต้องเปิด/ปิด
        self.confirm_button = None
        self.ship_button = None
        self.deliver_button = None
        self.cancel_button = None
        self.view_slip_button = None
        
        # สร้างหน้าจอ UI ทันที
        self.setup_ui() 
    
    def on_show(self):
        """
        ทำงานทุกครั้งที่เปิดหน้านี้:
        """
        self.load_orders() 
    
    # ============================================
    # ===== 1. "ผู้จัดการ" สร้าง UI หลัก =====
    # ============================================

    def setup_ui(self):
        """
        ฟังก์ชันหลักสำหรับสร้าง UI
        """
        self.grid_columnconfigure(0, weight=1) 
        self.grid_rowconfigure(1, weight=1)    

        # === 1.1 สร้างส่วนหัว (Header) ===
        self.create_header()
        
        # === 1.2 สร้าง Frame หลักสำหรับเนื้อหา (ตารางและปุ่ม) ===
        main_frame = ctk.CTkFrame(
            self, 
            fg_color="#FFFFFF", 
            corner_radius=20, 
            border_width=2, 
            border_color="#FFEBEE"
        )
        main_frame.grid(row=1, column=0, sticky="nsew", padx=30, pady=20) 
        main_frame.grid_columnconfigure(0, weight=1) 
        main_frame.grid_rowconfigure(1, weight=1) 
        
        # === 1.3 สร้าง Title ของตาราง ===
        title_frame = ctk.CTkFrame(main_frame, fg_color="#FFE4E1", corner_radius=15)
        title_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=20) 
        ctk.CTkLabel(
            title_frame,
            # ### <<< แก้ไขเล็กน้อย >>> ###
            text="📋 รายการคำสั่งซื้อ (ดับเบิ้ลคลิก: ดูใบเสร็จ | คลิก: เลือกออเดอร์)", 
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#6D4C41"
        ).pack(pady=15)
        
        # === 1.4 สร้างตาราง (Treeview) ===
        self.create_treeview(main_frame)
        
        # === 1.5 สร้างปุ่มควบคุม (Action Buttons) ===
        self.create_action_buttons(main_frame)
        
        # === 1.6 โหลดข้อมูลครั้งแรก (หลังจากสร้าง UI เสร็จ) ===
        self.load_orders() 

    # ============================================
    # ===== 2. "ผู้ช่วย" สร้างส่วนประกอบ UI =====
    # ============================================
    
    def create_header(self):
        """ สร้างส่วนหัว (Header) ของหน้า"""
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
        
        ctk.CTkLabel(
            header,
            text="📦 จัดการคำสั่งซื้อ",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#FFB6C1"
        ).pack(side="left", padx=30, pady=20)
        
        header_btn_frame = ctk.CTkFrame(header, fg_color="transparent")
        header_btn_frame.pack(side="right", padx=20)
        
        ctk.CTkButton(
            header_btn_frame,
            text="🏠 หน้าหลัก",
            command=lambda: self.main_app.navigate_to('HomeWindow'), 
            fg_color="transparent",
            text_color="#FFB6C1",
            hover_color="#FFE4E1",
            font=ctk.CTkFont(size=14)
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            header_btn_frame,
            text="📊 Dashboard",
            command=lambda: self.main_app.navigate_to('AdminDashboardWindow'), 
            fg_color="#4CAF50",
            hover_color="#66BB6A",
            font=ctk.CTkFont(size=14)
        ).pack(side="left", padx=5)

    def create_treeview(self, parent_frame):
        """สร้างตาราง Treeview และ Scrollbar ภายใน parent_frame"""
        tree_frame = ctk.CTkFrame(parent_frame, fg_color="transparent")
        tree_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20)) 
        tree_frame.grid_columnconfigure(0, weight=1) 
        tree_frame.grid_rowconfigure(0, weight=1) 
        
        style = ttk.Style()
        style.configure("Orders.Treeview", rowheight=40, font=('Arial', 12)) 
        style.configure("Orders.Treeview.Heading", font=('Arial', 13, 'bold')) 
        
        columns = ("order_id", "customer", "amount", "payment", "status", "date") 
        self.tree = ttk.Treeview(tree_frame, 
                                 columns=columns, 
                                 show="headings", 
                                 style="Orders.Treeview")
        
        self.tree.heading("order_id", text="Order ID")
        self.tree.heading("customer", text="ลูกค้า")
        self.tree.heading("amount", text="ยอดเงิน")
        self.tree.heading("payment", text="การชำระเงิน")
        self.tree.heading("status", text="สถานะ")
        self.tree.heading("date", text="วันที่")
        
        self.tree.column("order_id", width=80, anchor="center")
        self.tree.column("customer", width=200, anchor="w")
        self.tree.column("amount", width=120, anchor="e")
        self.tree.column("payment", width=150, anchor="w")
        self.tree.column("status", width=120, anchor="center")
        self.tree.column("date", width=150, anchor="center")
        
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set) 
        
        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        # ผูกอีเวนต์การดับเบิ้ลคลิก (สำหรับเปิดใบเสร็จ)
        self.tree.bind("<Double-1>", self.on_order_select_receipt)
        
        # ผูกอีเวนต์การคลิก (สำหรับเปิด/ปิดปุ่ม)
        self.tree.bind("<<TreeviewSelect>>", self.on_row_select)

    def create_action_buttons(self, parent_frame):
        """สร้างปุ่มควบคุมทั้งหมด (6 ปุ่ม)"""
        action_btn_frame = ctk.CTkFrame(parent_frame, fg_color="transparent")
        action_btn_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 20)) 
        
        # --- 1. ปุ่ม "ยืนยันคำสั่งซื้อ" ---
        self.confirm_button = ctk.CTkButton(
            action_btn_frame,
            text="✅ ยืนยันคำสั่งซื้อ",
            command=self.confirm_selected_order, 
            fg_color="#4CAF50",
            hover_color="#66BB6A",
            height=40,
            corner_radius=10,
            font=ctk.CTkFont(size=14, weight="bold"),
            state="disabled" # ### <<< เพิ่มใหม่ >>> ###
        )
        self.confirm_button.pack(side="left", padx=5, fill="x", expand=True) 
        
        # --- 2. ปุ่ม "เริ่มจัดส่ง" ---
        self.ship_button = ctk.CTkButton(
            action_btn_frame,
            text="🚚 เริ่มจัดส่ง",
            command=self.ship_selected_order,
            fg_color="#2196F3",
            hover_color="#42A5F5",
            height=40,
            corner_radius=10,
            font=ctk.CTkFont(size=14, weight="bold"),
            state="disabled" # ### <<< เพิ่มใหม่ >>> ###
        )
        self.ship_button.pack(side="left", padx=5, fill="x", expand=True)
        
        # --- 3. ปุ่ม "จัดส่งสำเร็จ" ---
        self.deliver_button = ctk.CTkButton(
            action_btn_frame,
            text="✔️ จัดส่งสำเร็จ",
            command=self.deliver_selected_order,
            fg_color="#FF9800",
            hover_color="#FFA726",
            height=40,
            corner_radius=10,
            font=ctk.CTkFont(size=14, weight="bold"),
            state="disabled" # ### <<< เพิ่มใหม่ >>> ###
        )
        self.deliver_button.pack(side="left", padx=5, fill="x", expand=True)
        
        # ### <<< เพิ่มใหม่ >>> ###
        # --- 4. ปุ่ม "ยกเลิกออเดอร์" ---
        self.cancel_button = ctk.CTkButton(
            action_btn_frame,
            text="❌ ยกเลิกออเดอร์",
            command=self.cancel_selected_order, 
            fg_color="#F44336", # สีแดง
            hover_color="#D32F2F",
            height=40,
            corner_radius=10,
            font=ctk.CTkFont(size=14, weight="bold"),
            state="disabled"
        )
        self.cancel_button.pack(side="left", padx=5, fill="x", expand=True)
        
        # --- 5. ปุ่ม "ดูสลิป" ---
        self.view_slip_button = ctk.CTkButton(
            action_btn_frame,
            text="📷 ดูสลิป",
            command=self.view_selected_slip, 
            fg_color="#9C27B0", # สีม่วง
            hover_color="#BA68C8",
            height=40,
            corner_radius=10,
            font=ctk.CTkFont(size=14, weight="bold"),
            state="disabled"
        )
        self.view_slip_button.pack(side="left", padx=5, fill="x", expand=True)

        # --- 6. ปุ่ม "รีเฟรช" (ปุ่มนี้เปิดตลอด) ---
        refresh_button = ctk.CTkButton(
            action_btn_frame,
            text="🔄 รีเฟรช",
            command=self.load_orders, 
            fg_color="#FFB6C1",
            hover_color="#FFC0CB",
            height=40,
            corner_radius=10,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        refresh_button.pack(side="left", padx=5, fill="x", expand=True)

    # ============================================
    # ===== 3. ฟังก์ชันจัดการข้อมูล (Data) =====
    # ============================================

    def on_row_select(self, event):
        """
        ถูกเรียกเมื่อผู้ใช้ 'คลิกเลือก' แถว
        ใช้เพื่อเปิด/ปิดการใช้งานปุ่มทั้งหมด
        """
        selected_item_id = self.tree.selection()
        
        # ถ้าไม่มีแถวไหนถูกเลือก ให้ปิดปุ่ม
        if not selected_item_id:
            self.disable_all_action_buttons()
            return
        
        # ถ้ามีแถวถูกเลือก ให้เปิดปุ่ม
        self.confirm_button.configure(state="normal")
        self.ship_button.configure(state="normal")
        self.deliver_button.configure(state="normal")
        self.cancel_button.configure(state="normal")
        self.view_slip_button.configure(state="normal")


    def on_order_select_receipt(self, event):
        """
        ถูกเรียกเมื่อผู้ใช้ 'ดับเบิ้ลคลิก' ที่ออเดอร์
        เพื่อเปิดหน้าใบเสร็จ (ReceiptWindow)
        """
        selected_item = self.tree.focus() 
        if not selected_item:
            return

        values = self.tree.item(selected_item, 'values')
        if not values:
            return

        try:
            order_id_str = values[0].lstrip('#')
            order_id = int(order_id_str)
            print(f"กำลังเปิดใบเสร็จสำหรับ Order ID: {order_id}")
            self.main_app.navigate_to('ReceiptWindow', order_id=order_id)

        except ValueError:
            messagebox.showerror("ผิดพลาด", f"Order ID ไม่ถูกต้อง: {values[0]}", parent=self)
        except Exception as e:
            messagebox.showerror("ผิดพลาด", f"เกิดข้อผิดพลาด ao-osr: {e}", parent=self)

    
    def get_selected_order_data_from_db(self):
        """
        (ฟังก์ชันช่วย) ดึงข้อมูล order_id จากแถวที่เลือก
        และ query ข้อมูลทั้งหมดจาก DB
        """
        selected_item_id = self.tree.selection()
        if not selected_item_id:
            messagebox.showwarning("คำเตือน", "กรุณาเลือกคำสั่งซื้อก่อน", parent=self)
            return None
        
        selected_item_id = selected_item_id[0]
        
        item_values = self.tree.item(selected_item_id)['values']
        if not item_values:
            return None
            
        try:
            order_id_str = item_values[0].lstrip('#')
            order_id = int(order_id_str)
        except (ValueError, IndexError):
            messagebox.showerror("ผิดพลาด", "ไม่สามารถอ่าน Order ID จากตารางได้", parent=self)
            return None
        
        order_data = self.db.get_order_details(order_id)
        
        if not order_data:
            messagebox.showerror("ผิดพลาด", f"ไม่พบข้อมูลสำหรับ Order ID: {order_id}", parent=self)
            return None
        
        return order_data

    def load_orders(self):
        """โหลดข้อมูลคำสั่งซื้อทั้งหมดมาใส่ตาราง"""
        if not self.tree: 
            return
            
        for item_id in self.tree.get_children():
            self.tree.delete(item_id)
        
        orders_data = self.db.get_all_orders()
        
        status_text_map = {
            'pending': '⏳ รอดำเนินการ',
            'confirmed': '✅ ยืนยันแล้ว',
            'shipped': '🚚 กำลังจัดส่ง',
            'delivered': '✔️ จัดส่งสำเร็จ',
            'cancelled': '❌ ยกเลิก'
        }
        
        for order in orders_data:
            status_display = status_text_map.get(order['status'], order['status'])
            
            order_date = order['created_at']
            if order_date:
                if hasattr(order_date, 'strftime'):
                    order_date = order_date.strftime('%Y-%m-%d %H:%M')
                elif len(order_date) > 16:
                    order_date = order_date[:16] 
            else:
                order_date = '-'
                
            self.tree.insert("", "end", values=(
                f"#{order['order_id']}",
                order['full_name'],
                f"฿{order['total_amount']:,.2f}",
                order['payment_method'],
                status_display,
                order_date
            ))
            
        # ปิดการใช้งานปุ่มทั้งหมดหลังจากโหลดข้อมูลใหม่
        self.disable_all_action_buttons()
    
    def change_status(self, new_status):
        """
        (ฟังก์ชันแกนกลาง) เปลี่ยนสถานะของคำสั่งซื้อที่เลือกในตาราง
        """
        selected_item_ids = self.tree.selection() 
        
        if not selected_item_ids:
            messagebox.showwarning("คำเตือน", "กรุณาเลือกคำสั่งซื้อที่ต้องการเปลี่ยนสถานะ", parent=self)
            return 
        
        status_names_map = {
            'confirmed': 'ยืนยันคำสั่งซื้อ',
            'shipped': 'เริ่มจัดส่ง',
            'delivered': 'จัดส่งสำเร็จ',
            'cancelled': 'ยกเลิก'
        }
        status_name_thai = status_names_map.get(new_status, new_status)
        confirm_message = f"ต้องการเปลี่ยนสถานะ {len(selected_item_ids)} รายการ เป็น '{status_name_thai}' ใช่หรือไม่?"
        
        # ### <<< เพิ่มใหม่ >>> ###
        # เพิ่มไอคอนเตือนสำหรับ "ยกเลิก"
        icon_type = "warning" if new_status == 'cancelled' else "question"
        
        user_confirmed = messagebox.askyesno("ยืนยัน", confirm_message, icon=icon_type, parent=self)
        
        if user_confirmed:
            success_count = 0
            fail_count = 0
            
            for item_id in selected_item_ids:
                try:
                    item_values = self.tree.item(item_id)['values']
                    order_id_str = item_values[0] 
                    order_id = int(order_id_str.replace('#', '')) 
                    
                    success = self.db.update_order_status(order_id, new_status)
                    
                    if success:
                        success_count += 1
                    else:
                        fail_count += 1
                except Exception:
                     fail_count += 1
            
            if fail_count > 0:
                 messagebox.showerror("ผิดพลาด", f"ไม่สามารถเปลี่ยนสถานะได้ {fail_count} รายการ", parent=self)
            if success_count > 0:
                messagebox.showinfo("สำเร็จ", f"เปลี่ยนสถานะ {success_count} รายการเรียบร้อย!", parent=self)
            
            # โหลดข้อมูลตารางใหม่ (ซึ่งจะปิดปุ่มทั้งหมด)
            self.load_orders()
        else:
            # ถ้าผู้ใช้กดยกเลิก (No)
            # ให้เคลียร์ selection และปิดปุ่ม
            for item in selected_item_ids:
                self.tree.selection_remove(item)
            self.disable_all_action_buttons()


    # =================================================================
    # ===== 4. ฟังก์ชันสำหรับปุ่ม =====
    # =================================================================

    def confirm_selected_order(self):
        self.change_status("confirmed")

    def ship_selected_order(self):
        self.change_status("shipped")

    def deliver_selected_order(self):
        self.change_status("delivered")
    
    # ### <<< เพิ่มใหม่ >>> ###
    def cancel_selected_order(self):
        self.change_status("cancelled")
        
    # ### <<< เพิ่มใหม่ >>> ###
    def disable_all_action_buttons(self):
        """(ฟังก์ชันช่วย) ปิดการใช้งานปุ่ม action ทั้งหมด"""
        if self.confirm_button:
            self.confirm_button.configure(state="disabled")
        if self.ship_button:
            self.ship_button.configure(state="disabled")
        if self.deliver_button:
            self.deliver_button.configure(state="disabled")
        if self.cancel_button:
            self.cancel_button.configure(state="disabled")
        if self.view_slip_button:
            self.view_slip_button.configure(state="disabled")
    
    def view_selected_slip(self):
        """
        (ปุ่ม 5) เปิดหน้าต่างใหม่เพื่อแสดงสลิปที่แนบมา
        """
        order_data = self.get_selected_order_data_from_db()
        if not order_data:
            return 
        
        slip_filename = order_data.get('slip_image_url')
        
        if not slip_filename:
            messagebox.showinfo("ไม่มีสลิป", "คำสั่งซื้อนี้ไม่มีการแนบสลิป\n(อาจเป็น COD หรือยังไม่อัปโหลด)", parent=self)
            return
        
        try:
            # *** ⚠️ สมมติฐาน: สลิปถูกเก็บไว้ใน "assets/slips/" ***
            slip_path = os.path.join(self.main_app.base_path, "assets", "slips", slip_filename)
            
            if not os.path.exists(slip_path):
                messagebox.showerror("ไม่พบไฟล์", f"ไม่พบไฟล์สลิป: {slip_filename}\nที่: {slip_path}", parent=self)
                return
            
            self.show_slip_window(slip_path, order_data)
            
        except Exception as e:
            messagebox.showerror("ผิดพลาด", f"ไม่สามารถเปิดไฟล์สลิปได้: {e}", parent=self)

            
    def show_slip_window(self, image_path, order_data):
        """สร้างหน้าต่าง Toplevel เพื่อแสดงรูปภาพสลิป"""
        
        if self.slip_win and self.slip_win.winfo_exists():
            self.slip_win.lift() 
            return

        self.slip_win = ctk.CTkToplevel(self)
        self.slip_win.title(f"สลิปสำหรับ Order #{order_data['order_id']}")
        self.slip_win.geometry("500x700")
        self.slip_win.grab_set() 
        
        self.slip_win.protocol("WM_DELETE_WINDOW", self.on_slip_window_close)
        
        self.slip_win.grid_columnconfigure(0, weight=1)
        self.slip_win.grid_rowconfigure(1, weight=1)

        # --- 1. กรอบข้อมูล (สำหรับเปรียบเทียบ) ---
        info_frame = ctk.CTkFrame(self.slip_win, fg_color="#F0F0F0")
        info_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        info_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(info_frame, text="ชื่อลูกค้า:", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=10, pady=5, sticky="e")
        ctk.CTkLabel(info_frame, text=f"{order_data.get('full_name', 'N/A')}", anchor="w").grid(row=0, column=1, padx=10, pady=5, sticky="w")
        
        ctk.CTkLabel(info_frame, text="ยอดที่ต้องชำระ:", font=ctk.CTkFont(weight="bold")).grid(row=1, column=0, padx=10, pady=5, sticky="e")
        ctk.CTkLabel(info_frame, text=f"฿{order_data.get('total_amount', 0):,.2f}", 
                     text_color="#E91E63", 
                     font=ctk.CTkFont(size=16, weight="bold"), 
                     anchor="w").grid(row=1, column=1, padx=10, pady=5, sticky="w")
        
        # --- 2. กรอบรูปภาพ (เลื่อนได้) ---
        scroll_frame = ctk.CTkScrollableFrame(self.slip_win, fg_color="#FFFFFF")
        scroll_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        
        # --- 3. โหลดและแสดงรูปภาพ ---
        try:
            pil_image = Image.open(image_path)
            
            window_width = 460 
            img_w, img_h = pil_image.size
            
            scale = window_width / img_w
            new_height = int(img_h * scale)
            
            ctk_image = ctk.CTkImage(light_image=pil_image, size=(window_width, new_height))
            
            image_label = ctk.CTkLabel(scroll_frame, image=ctk_image, text="")
            image_label.pack(expand=True, fill="both", padx=5, pady=5)
            
        except Exception as e:
            ctk.CTkLabel(scroll_frame, text=f"ไม่สามารถโหลดรูปภาพได้:\n{e}", text_color="red").pack(pady=20)
            
    def on_slip_window_close(self):
        """
        ถูกเรียกเมื่อปิดหน้าต่างดูสลิป
        """
        self.slip_win.destroy()
        self.slip_win = None