# M:/doll_shop/main.py (Added load_profile_image function and necessary imports/frames)

import customtkinter as ctk
from PIL import Image, ImageTk # Import ImageTk if needed for CTkImage fallback
import os
import sys # Import sys for platform check (PDF opening)
import subprocess # Import subprocess for PDF opening
from database import Database
from models import Session, User, Cart, Order, Product # Import necessary models
# --- UI Imports (Ensure all necessary classes are imported) ---
from ui_login import LoginWindow
from ui_home import HomeWindow
from ui_admin import AdminWindow
from ui_admin_dashboard import AdminDashboardWindow
from ui_cart import CartWindow
from ui_checkout import CheckoutWindow
from ui_order_history import OrderHistoryWindow
from ui_product_list import ProductListWindow
from ui_admin_orders import AdminOrdersWindow
from ui_profile import ProfileWindow
from ui_thankyou import ThankYouWindow
from ui_receipt import ReceiptWindow
from ui_about import AboutWindow
from ui_sales_history import SalesHistoryWindow
from ui_admin_users import AdminUsersWindow  # <--- (เพิ่มบรรทัดนี้)


class MainApplication(ctk.CTk):
    """
    คลาสหลักสำหรับหน้าต่างโปรแกรม
    """
    def __init__(self):
        super().__init__()
        self.title("🎀 Dollie Shop 🎀")
        self.geometry("1280x800")
        self.minsize(1024, 768)
        ctk.set_appearance_mode("light")

        try:
            self.db = Database() # Database object handles its own path now
        except Exception as db_init_error:
            print(f"!!! CRITICAL ERROR: Failed to initialize Database: {db_init_error}")
            # Show error and exit if DB fails
            messagebox.showerror("Database Error", f"Could not connect to or create the database:\n{db_init_error}\n\nApplication will exit.")
            sys.exit(1) # Exit the application

        self.session = Session()
        self.cart = Cart()
        # Get the directory where main.py is located
        self.base_path = os.path.dirname(os.path.abspath(__file__))
        print(f"Main application base path: {self.base_path}") # Debug path

        container_frame = ctk.CTkFrame(self, fg_color="transparent")
        container_frame.pack(side="top", fill="both", expand=True)
        container_frame.grid_rowconfigure(0, weight=1)
        container_frame.grid_columnconfigure(0, weight=1)

        self.all_app_frames = {}

        # --- Create all UI Frames (Ensure all classes are instantiated) ---
        # List of all window classes to instantiate (filter out None placeholders)
        all_window_classes = [
            LoginWindow, HomeWindow, AdminWindow, AdminDashboardWindow, CartWindow,
            CheckoutWindow, OrderHistoryWindow, ProductListWindow, AdminOrdersWindow,
            ProfileWindow, ThankYouWindow, ReceiptWindow, AboutWindow, SalesHistoryWindow,
            AdminUsersWindow  # <--- (เพิ่มบรรทัดนี้)
        ]
        # Filter out None values in case some files were missing
        valid_window_classes = [cls for cls in all_window_classes if cls is not None]

        for WindowClass in valid_window_classes:
            page_name = WindowClass.__name__
            try:
                frame_instance = WindowClass(parent=container_frame, main_app=self)
                self.all_app_frames[page_name] = frame_instance
                frame_instance.grid(row=0, column=0, sticky="nsew")
                print(f"Created frame: {page_name}")
            except Exception as e:
                print(f"!!! Error creating frame {page_name}: {e}")
                # Optional: Show error message to user, but continue startup
                # messagebox.showwarning("UI Error", f"Could not create window: {page_name}\n{e}")
                pass # Continue creating other frames

        print("Finished creating frames.")

        # --- Start with Login page ---
        if "LoginWindow" in self.all_app_frames:
             self.navigate_to("LoginWindow")
        else:
             print("!!! CRITICAL ERROR: LoginWindow could not be created. Cannot start application.")
             error_label = ctk.CTkLabel(self, text="Fatal Error: Could not initialize Login screen.", text_color="red", font=("Arial", 16))
             error_label.pack(expand=True)
             # Exit if login screen fails
             # sys.exit(1)


    # --- Image Loading Functions ---
    def load_image(self, image_filename, size):
        """Loads an image from the 'assets' folder relative to main.py."""
        if not image_filename: # Handle None filename gracefully
             print("!!! Warning: load_image called with None filename. Returning placeholder.")
             placeholder_image = Image.new('RGBA', size, color = (192, 192, 192, 255))
             ctk_placeholder = ctk.CTkImage(light_image=placeholder_image, dark_image=placeholder_image, size=size)
             return ctk_placeholder

        image_path = os.path.join(self.base_path, "assets", image_filename)
        # print(f"Attempting to load image: {image_path}") # Debug message
        try:
            pil_image = Image.open(image_path)
            # Ensure image is in a compatible mode (RGBA)
            pil_image = pil_image.convert("RGBA")
            # Use light_image and dark_image for CTkImage
            ctk_image = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=size)
            # print(f"Successfully loaded image: {image_filename}") # Debug message
            return ctk_image
        except FileNotFoundError:
             print(f"!!! Error loading image: File not found at '{image_path}'")
             # Return placeholder if file not found
             placeholder_image = Image.new('RGBA', size, color = (192, 192, 192, 255)) # Light gray RGBA
             ctk_placeholder = ctk.CTkImage(light_image=placeholder_image, dark_image=placeholder_image, size=size)
             return ctk_placeholder
        except Exception as e:
            print(f"!!! General Error loading image '{image_filename}': {e}")
            # Return placeholder on other errors
            placeholder_image = Image.new('RGBA', size, color = (255, 0, 0, 255)) # Red RGBA indicates error
            ctk_placeholder = ctk.CTkImage(light_image=placeholder_image, dark_image=placeholder_image, size=size)
            return ctk_placeholder


    def get_product_image(self, product_image_filename, size=(200, 200)):
        """Loads a product image from 'assets/images', uses placeholder on failure."""
        placeholder_img = self.load_image("placeholder.png", size) # Load placeholder via load_image
        if not product_image_filename:
            return placeholder_img
        image_path = os.path.join(self.base_path, "assets", "images", product_image_filename)
        # print(f"Attempting to load product image: {image_path}") # Debug message
        try:
            pil_product_image = Image.open(image_path)
            pil_product_image = pil_product_image.convert("RGBA")
            ctk_product_image = ctk.CTkImage(light_image=pil_product_image, dark_image=pil_product_image, size=size)
            return ctk_product_image
        except FileNotFoundError:
             print(f"Product image '{product_image_filename}' not found, using placeholder.")
             return placeholder_img
        except Exception as e:
            print(f"!!! Error loading product image '{product_image_filename}': {e}, using placeholder.")
            return placeholder_img

    def load_profile_image(self, profile_image_filename, size=(100, 100)):
        """
        Loads a profile picture from assets/profile_pics.
        Returns the default profile picture if file not found or filename is None/empty.
        """
        default_icon_filename = "default_profile.png" # Must exist in 'assets' folder

        # Load default image first (will act as fallback)
        default_img = self.load_image(default_icon_filename, size)

        if not profile_image_filename: # If no specific filename, return default
            return default_img

        # Construct path to the specific profile picture in 'assets/profile_pics'
        profile_image_path = os.path.join(self.base_path, "assets", "profile_pics", profile_image_filename)
        # print(f"Attempting to load profile image: {profile_image_path}") # Debug message
        try:
            pil_profile_image = Image.open(profile_image_path)
            pil_profile_image = pil_profile_image.convert("RGBA")
            ctk_profile_image = ctk.CTkImage(light_image=pil_profile_image, dark_image=pil_profile_image, size=size)
            # print(f"Successfully loaded profile image: {profile_image_filename}") # Debug message
            return ctk_profile_image
        except FileNotFoundError:
            print(f"Profile image '{profile_image_filename}' not found, using default.")
            return default_img # Return the already loaded default
        except Exception as e:
            print(f"!!! Error loading profile image '{profile_image_filename}': {e}, using default.")
            return default_img # Return the already loaded default

    # --- Navigation and Callbacks ---
    def navigate_to(self, target_page_name, **extra_data):
        """Switches the visible frame and calls its on_show method."""
        print(f"Navigating to: {target_page_name}, Data: {extra_data}")
        target_frame = self.all_app_frames.get(target_page_name)
        if not target_frame:
            print(f"!!! Error: Frame '{target_page_name}' not found!")
            # Maybe navigate to a default page like Home or show an error
            if "HomeWindow" in self.all_app_frames:
                 print("Navigating to HomeWindow as fallback.")
                 self.navigate_to("HomeWindow")
            else:
                 messagebox.showerror("Navigation Error", f"Window '{target_page_name}' not found.")
            return

        # --- Call on_show if it exists ---
        if hasattr(target_frame, 'on_show') and callable(getattr(target_frame, 'on_show')):
            try:
                target_frame.on_show(**extra_data)
                print(f"Called on_show() for {target_page_name}")
            except TypeError as te:
                 # Handle cases where on_show doesn't accept the extra_data
                 print(f"!!! Warning: TypeError calling on_show() for {target_page_name}: {te}. Trying without data.")
                 try:
                      target_frame.on_show() # Try calling without arguments
                 except Exception as e_inner:
                      print(f"!!! Error calling on_show() for {target_page_name} even without data: {e_inner}")
            except Exception as e:
                print(f"!!! Error calling on_show() for {target_page_name}: {e}")
        else:
             print(f"Frame {target_page_name} has no on_show() method.")

        # --- Raise the target frame to the top ---
        target_frame.tkraise()

    def on_login_success(self, user_data_dict):
        """Called by LoginWindow on successful login."""
        # Add checks for necessary keys in user_data_dict
        required_keys = ['user_id', 'username', 'email', 'full_name']
        if not user_data_dict or not all(key in user_data_dict for key in required_keys):
             print(f"!!! Error: Incomplete user data received on login: {user_data_dict}")
             messagebox.showerror("Login Error", "Received incomplete user data from database.")
             self.navigate_to("LoginWindow") # Go back to login
             return

        try:
            user_object = User.from_dict(user_data_dict)
            if user_object is None: # Check if from_dict failed
                 raise ValueError("User.from_dict returned None")
            self.session.login(user_object)
            print(f"Login successful: User: {user_object.username}, Role: {user_object.role}")
            self.navigate_to("HomeWindow")
        except Exception as e:
            print(f"!!! Unexpected error during on_login_success: {e}")
            messagebox.showerror("Login Error", f"An unexpected error occurred during login:\n{e}")
            self.navigate_to("LoginWindow")


    def on_logout(self):
        """Called when the logout button is pressed."""
        self.session.logout()
        self.cart.clear()
        print("User logged out.")
        self.navigate_to("LoginWindow")

# --- Start the Application ---
if __name__ == "__main__":
    try:
        # --- Ensure assets directory exists ---
        # Get base path relative to this script file
        app_base_path = os.path.dirname(os.path.abspath(__file__))
        assets_path = os.path.join(app_base_path, "assets")
        profile_pics_path = os.path.join(assets_path, "profile_pics")
        images_path = os.path.join(assets_path, "images")
        slips_path = os.path.join(assets_path, "slips") # Added for slips

        if not os.path.isdir(assets_path):
             print(f"!!! WARNING: 'assets' directory not found at {assets_path}. Creating it.")
             os.makedirs(assets_path, exist_ok=True)
        if not os.path.isdir(profile_pics_path):
             print(f"!!! WARNING: 'profile_pics' directory not found at {profile_pics_path}. Creating it.")
             os.makedirs(profile_pics_path, exist_ok=True)
        if not os.path.isdir(images_path):
             print(f"!!! WARNING: 'images' directory not found at {images_path}. Creating it.")
             os.makedirs(images_path, exist_ok=True)
        if not os.path.isdir(slips_path):
             print(f"!!! WARNING: 'slips' directory not found at {slips_path}. Creating it.")
             os.makedirs(slips_path, exist_ok=True)

        # --- Check for default profile image ---
        default_profile_path = os.path.join(assets_path, "default_profile.png")
        if not os.path.exists(default_profile_path):
             print(f"!!! WARNING: Default profile image 'default_profile.png' not found in assets directory.")
             # Optionally create a dummy placeholder if missing?

        app = MainApplication()
        app.mainloop()
    except Exception as start_error:
        print(f"!!! Application failed to start: {start_error}")
        # Show a simple Tkinter error box
        import tkinter as tk
        from tkinter import messagebox # Ensure messagebox is imported here too
        try:
            root = tk.Tk()
            root.withdraw() # Hide the main Tk window
            messagebox.showerror("Application Startup Error", f"Failed to start Dollie Shop:\n{start_error}")
            root.destroy()
        except Exception as msg_err:
             print(f"Could not display Tkinter error message: {msg_err}")
        sys.exit(1) # Exit with error code