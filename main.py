# M:/doll_shop/main.py (Added load_profile_image and necessary imports/frames)

import customtkinter as ctk
from PIL import Image
import os
from database import Database
from models import Session, User, Cart
# --- UI Imports (Ensure all are present) ---
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

        self.db = Database() # Database object handles its own path now
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
        # List of all window classes to instantiate
        all_window_classes = [
            LoginWindow, HomeWindow, AdminWindow, AdminDashboardWindow, CartWindow,
            CheckoutWindow, OrderHistoryWindow, ProductListWindow, AdminOrdersWindow,
            ProfileWindow, ThankYouWindow, ReceiptWindow, AboutWindow, SalesHistoryWindow,
        ]

        for WindowClass in all_window_classes:
            page_name = WindowClass.__name__ # Get class name as string (e.g., "LoginWindow")
            try:
                frame_instance = WindowClass(parent=container_frame, main_app=self)
                self.all_app_frames[page_name] = frame_instance
                # Place the frame in the grid, it will be raised later by navigate_to
                frame_instance.grid(row=0, column=0, sticky="nsew")
                print(f"Created frame: {page_name}")
            except Exception as e:
                print(f"!!! Error creating frame {page_name}: {e}")
                # Decide how to handle this - maybe skip or raise error?
                # For robustness, let's skip the problematic frame for now
                pass # Continue creating other frames

        print("Finished creating frames.")

        # --- Start with Login page ---
        # Check if LoginWindow was created successfully before navigating
        if "LoginWindow" in self.all_app_frames:
             self.navigate_to("LoginWindow")
        else:
             print("!!! CRITICAL ERROR: LoginWindow could not be created. Cannot start application.")
             # You might want to show an error message directly on the root window here
             error_label = ctk.CTkLabel(self, text="Fatal Error: Could not initialize Login screen.", text_color="red", font=("Arial", 16))
             error_label.pack(expand=True)


    # --- Image Loading Functions ---
    def load_image(self, image_filename, size):
        """Loads an image from the 'assets' folder."""
        # Construct path relative to main.py's location
        image_path = os.path.join(self.base_path, "assets", image_filename)
        # print(f"Attempting to load image: {image_path}") # Debug message
        try:
            pil_image = Image.open(image_path)
            pil_image = pil_image.convert("RGBA") # Ensure alpha channel
            ctk_image = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=size) # Use light/dark
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
        placeholder_img = self.load_image("placeholder.png", size)
        if not product_image_filename:
            return placeholder_img
        # Construct path relative to main.py's location
        product_image_path = os.path.join(self.base_path, "assets", "images", product_image_filename)
        # print(f"Attempting to load product image: {product_image_path}") # Debug message
        try:
            pil_product_image = Image.open(product_image_path)
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
        Returns the default profile picture if the file is not found or filename is None/empty.
        """
        default_icon = "default_profile.png" # Must exist in 'assets' folder

        # Load default image first (will act as fallback)
        default_img = self.load_image(default_icon, size)

        # If no specific filename, return the default immediately
        if not profile_image_filename:
            return default_img

        # Construct path to the specific profile picture
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
            return

        # --- Call on_show if it exists ---
        if hasattr(target_frame, 'on_show') and callable(getattr(target_frame, 'on_show')):
            try:
                target_frame.on_show(**extra_data)
                print(f"Called on_show() for {target_page_name}")
            except Exception as e:
                print(f"!!! Error calling on_show() for {target_page_name}: {e}")
        else:
             print(f"Frame {target_page_name} has no on_show() method.")

        # --- Raise the target frame to the top ---
        target_frame.tkraise()

    def on_login_success(self, user_data_dict):
        """Called by LoginWindow on successful login."""
        try:
            user_object = User.from_dict(user_data_dict)
            self.session.login(user_object)
            print(f"Login successful: User: {user_object.username}, Role: {user_object.role}")
            self.navigate_to("HomeWindow")
        except KeyError as e:
             print(f"!!! Error processing user data on login: Missing key {e}")
             # Optionally show error to user or navigate back to login
             # messagebox.showerror("Login Error", "Failed to process user data.")
             self.navigate_to("LoginWindow") # Go back to login on error
        except Exception as e:
            print(f"!!! Unexpected error during on_login_success: {e}")
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
        app = MainApplication()
        app.mainloop()
    except Exception as start_error:
        print(f"!!! Application failed to start: {start_error}")
        # Show a simple Tkinter error box if CTk fails early
        import tkinter as tk
        root = tk.Tk()
        root.withdraw() # Hide the main Tk window