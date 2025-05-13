import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import random
import psycopg2
from psycopg2 import sql, errors


DB_CONFIG = {
    "dbname": "py_prj",
    "user": "postgres",
    "password": "mane1010",
    "host": "localhost",
    "port": "5432"
}


locations = ["Chennai", "Coimbatore", "Madurai", "Trichy", "Tirunelvelli"]
vehicle_types = {"Sedan": 500, "SUV": 800, "Truck": 1000}
car_models = {
    "Sedan": [("Toyota Camry", "sedan1.jpg", "Mileage: 28 mpg\nCondition: Excellent\nTransmission: Automatic"),
               ("Honda Accord", "sedan2.jfif", "Mileage: 30 mpg\nCondition: Good\nTransmission: Manual")],
    "SUV": [("Ford Explorer", "suv1.jfif", "Mileage: 24 mpg\nCondition: Excellent\nTransmission: Automatic"),
             ("Jeep Cherokee", "suv2.jfif", "Mileage: 22 mpg\nCondition: Good\nTransmission: Manual")],
    "Truck": [("Ford F-150", "truck1.jfif", "Mileage: 20 mpg\nCondition: Good\nTransmission: Manual"),
               ("Chevrolet Silverado", "truck2.jfif", "Mileage: 18 mpg\nCondition: Excellent\nTransmission: Automatic")]
}

base_cost = 0
gst = 0
total_cost = 0
token_number = random.randint(1000, 9999)

def update_models(event):
    selected_type = vehicle_type_var.get()
    model_dropdown["values"] = [m[0] for m in car_models.get(selected_type, [])]
    model_var.set("")
    update_cost()
    update_car_preview()


def update_car_preview(*args):
    for widget in preview_frame.winfo_children():
        widget.destroy()
    selected_type = vehicle_type_var.get()
    selected_model = model_var.get()
    if selected_type and selected_model:
        for model_info in car_models[selected_type]:
            if model_info[0] == selected_model:
                card = tk.Frame(preview_frame, bg="white", bd=2, relief="groove")
                card.pack(padx=10, pady=10, fill="both", expand=True)
                try:
                    image = Image.open(model_info[1])
                    image = image.resize((280, 160))
                    photo = ImageTk.PhotoImage(image)
                    img_label = tk.Label(card, image=photo, bg="white")
                    img_label.image = photo
                    img_label.pack(pady=5)
                except:
                    tk.Label(card, text="[Image Not Found]", bg="white").pack(pady=5)

                tk.Label(card, text=model_info[0], font=("Arial", 14, "bold"), bg="white").pack(pady=2)
                tk.Label(card, text=model_info[2], bg="white", font=("Arial", 11), justify="left").pack(pady=5)
                break

def update_cost(*args):
    global base_cost, gst, total_cost
    duration = duration_var.get()
    vehicle_type = vehicle_type_var.get()
    driver_required = driver_var.get()
    if vehicle_type and duration.isdigit():
        base_cost = vehicle_types[vehicle_type] * int(duration)
        driver_cost = 800 * int(duration) if driver_required else 0
        base_cost += driver_cost
        gst = base_cost * 0.18
        total_cost = base_cost + gst
        cost_label.config(text=f"Total Cost: Rs. {total_cost:.2f} (Incl. 18% GST)")
    else:
        cost_label.config(text="Please select all options correctly.")
def save_billing_to_db(token, name, phone, location, vehicle_type, model, duration, driver_required, base_cost, gst, total_cost):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS billing (
                token INTEGER PRIMARY KEY,
                name TEXT,
                phone TEXT,
                location TEXT,
                vehicle_type TEXT,
                model TEXT,
                duration INTEGER,
                driver_required TEXT,
                base_cost REAL,
                gst REAL,
                total_cost REAL
            )
        ''')

        cursor.execute('''
            INSERT INTO billing (token, name, phone, location, vehicle_type, model, duration, driver_required, base_cost, gst, total_cost)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (
            token, name, phone, location, vehicle_type, model,
            duration, "Yes" if driver_required else "No",
            base_cost, gst, total_cost
        ))

        conn.commit()
        cursor.close()
        conn.close()
        print(f"[✓] Billing info for token {token} saved to PostgreSQL.")
    except errors.UniqueViolation:
        messagebox.showerror("Database Error", f"Token {token} already exists. Please try again.")
    except Exception as e:
        messagebox.showerror("Database Error", str(e))


root = tk.Tk()
root.title("Car Rental Service")
root.geometry("700x550")
root.configure(bg="#f8f9fa")

header_frame = tk.Frame(root, bg="#343a40")
header_frame.pack(fill="x", side="top")
title_label = tk.Label(header_frame, text="Car Rental Service", fg="white", bg="#343a40", font=("Arial", 18, "bold"))
title_label.pack()
try:
    logo_img = Image.open("logo.png")  # Make sure logo.png is in the same directory
    logo_img = logo_img.resize((70, 70))
    logo_photo = ImageTk.PhotoImage(logo_img)
    tk.Label(header_frame, image=logo_photo, bg="#343a40").pack(side="top", padx=10)
except:
    pass


footer_frame_main = tk.Frame(root, bg="#343a40")
footer_frame_main.pack(fill="x", side="bottom")
cost_label = tk.Label(footer_frame_main, text="Total Cost: Rs. 0.00 (Incl. 18% GST)", font=("Arial", 12), bg="#343a40", fg="white")
cost_label.pack()

main_frame = tk.Frame(root, bg="#f8f9fa")
main_frame.pack(fill="both", expand=True, padx=10, pady=10)


options_frame = tk.Frame(main_frame, bg="#f8f9fa")
options_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
separator = tk.Frame(main_frame, bg="#dee2e6", width=2)
separator.grid(row=0, column=1, sticky="ns", padx=2)
preview_frame = tk.Frame(main_frame, bg="#f8f9fa")
preview_frame.grid(row=0, column=2, sticky="nsew", padx=(5, 0))



# Configure grid columns to give spacing
options_frame.columnconfigure(0, weight=1, pad=10)
options_frame.columnconfigure(1, weight=2, pad=10)

# Row 0: Location
tk.Label(options_frame, text="Select Location:", bg="#f8f9fa", font=("Arial", 12)).grid(row=0, column=0, sticky="w", pady=5)
location_var = tk.StringVar()
location_dropdown = ttk.Combobox(options_frame, textvariable=location_var, values=locations, width=25)
location_dropdown.grid(row=0, column=1, pady=5)

# Row 1: Vehicle Type
tk.Label(options_frame, text="Select Vehicle Type:", bg="#f8f9fa", font=("Arial", 12)).grid(row=1, column=0, sticky="w", pady=5)
vehicle_type_var = tk.StringVar()
vehicle_dropdown = ttk.Combobox(options_frame, textvariable=vehicle_type_var, values=list(vehicle_types.keys()), width=25)
vehicle_dropdown.grid(row=1, column=1, pady=5)
vehicle_dropdown.bind("<<ComboboxSelected>>", update_models)

# Row 2: Car Model
tk.Label(options_frame, text="Select Car Model:", bg="#f8f9fa", font=("Arial", 12)).grid(row=2, column=0, sticky="w", pady=5)
model_var = tk.StringVar()
model_dropdown = ttk.Combobox(options_frame, textvariable=model_var, width=25)
model_dropdown.grid(row=2, column=1, pady=5)
model_dropdown.bind("<<ComboboxSelected>>", update_car_preview)

# Row 3: Duration
tk.Label(options_frame, text="Duration (days):", bg="#f8f9fa", font=("Arial", 12)).grid(row=3, column=0, sticky="w", pady=5)
duration_var = tk.StringVar()
duration_var.trace("w", update_cost)
duration_entry = tk.Entry(options_frame, textvariable=duration_var, width=27)
duration_entry.grid(row=3, column=1, pady=5)

# Row 4: Driver Checkbox (spanning 2 columns
driver_var = tk.BooleanVar()
driver_check = tk.Checkbutton(options_frame, text="Driver Required (Rs. 800/day extra)", variable=driver_var, bg="#f8f9fa", command=update_cost)
driver_check.grid(row=4, column=0, columnspan=2, sticky="w", pady=10)

def open_about_page():
    about_page = tk.Toplevel(root)
    about_page.title("About Us - Car Rental Service")
    about_page.geometry("600x400")
    about_page.configure(bg="#f8f9fa")

    header_frame = tk.Frame(about_page, bg="#ffc107", pady=10)
    header_frame.pack(fill="x")
    tk.Label(header_frame, text="About Us", font=("Arial", 18, "bold"), bg="#ffc107").pack()

    about_text = "Welcome to Car Rental Service!\n\nWe provide the best car rental experience with a variety of vehicles to choose from. Whether you need a sedan for city driving, an SUV for a family trip, or a truck for transportation, we have you covered.\n\nOur service is available in multiple locations, and we ensure affordable pricing with transparent billing. Book your ride today!"
    tk.Label(about_page, text=about_text, font=("Arial", 12), bg="#f8f9fa", wraplength=550, justify="left").pack(pady=20)

    footer_frame = tk.Frame(about_page, bg="#ffc107", pady=10)
    footer_frame.pack(fill="x", side="bottom")
    tk.Label(footer_frame, text="© 2025 Car Rental Service", font=("Arial", 10), bg="#ffc107").pack()

    try:
        image = Image.open("car_display.jpg")
        image = image.resize((400, 200))
        img = ImageTk.PhotoImage(image)
        img_label = tk.Label(about_page, image=img, bg="#f8f9fa")
        img_label.image = img
        img_label.pack(pady=10)
    except:
        pass

def open_billing_page(name):
    bill_page = tk.Toplevel(root)
    bill_page.title("Rental Bill")
    bill_page.geometry("500x480")
    bill_page.configure(bg="#e9ecef")  # light background for contrast



    # Header section
    header = tk.Frame(bill_page, bg="#007bff", pady=12)
    header.pack(fill="x")
    tk.Label(header, text="Rental Receipt", font=("Arial", 18, "bold"), bg="#007bff", fg="white").pack()

    # Token number as separate highlight bar
    token_frame = tk.Frame(bill_page, bg="#ffffff")
    token_frame.pack(fill="x")
    tk.Label(token_frame, text=f"Rental Token #: {token_number}", font=("Arial", 12, "bold"),
             fg="#343a40", bg="#ffffff", pady=10).pack()

    # Main content section (white card)
    content_frame = tk.Frame(bill_page, bg="#ffffff", padx=20, pady=20, bd=1, relief="groove")
    content_frame.pack(padx=20, pady=20, fill="both", expand=True)

    def info_label(text, bold=False, green=False):
        return tk.Label(
            content_frame,
            text=text,
            font=("Arial", 12, "bold" if bold else "normal"),
            fg="#28a745" if green else "#212529",
            bg="#ffffff",
            anchor="w"
        )

    info_label(f"Customer Name: {name}").pack(anchor="w", pady=4)
    info_label(f"Location: {location_var.get()}").pack(anchor="w", pady=4)
    info_label(f"Vehicle: {vehicle_type_var.get()} - {model_var.get()}").pack(anchor="w", pady=4)
    info_label(f"Duration: {duration_var.get()} day(s)").pack(anchor="w", pady=4)
    if driver_var.get():
        info_label(f"Driver Cost: Rs. {800 * int(duration_var.get()):.2f}").pack(anchor="w", pady=4)
    info_label(f"Base Cost: Rs. {base_cost - gst:.2f}").pack(anchor="w", pady=4)
    info_label(f"GST (18%): Rs. {gst:.2f}").pack(anchor="w", pady=4)
    info_label(f"Total Amount: Rs. {total_cost:.2f}", bold=True, green=True).pack(anchor="w", pady=10)

    # Footer
    footer = tk.Frame(bill_page, bg="#007bff", pady=12)
    footer.pack(fill="x", side="bottom")
    tk.Label(footer, text="Thank you for choosing Car Rental Service!",
             font=("Arial", 10), bg="#007bff", fg="white").pack()

def open_payment_page():
    if not location_var.get() or not vehicle_type_var.get() or not model_var.get() or not duration_var.get():
        messagebox.showerror("Error", "Please fill in all fields before proceeding to payment.")
        return

    payment_page = tk.Toplevel(root)
    payment_page.title("Payment - Car Rental Service")
    payment_page.geometry("600x500")
    payment_page.configure(bg="#f8f9fa")

    header_frame = tk.Frame(payment_page, bg="#ffc107", pady=10)
    header_frame.pack(fill="x")
    tk.Label(header_frame, text="Payment", font=("Arial", 18, "bold"), bg="#ffc107").pack(side = "bottom", fill="x")

    tk.Label(payment_page, text="Enter your details to proceed with payment", font=("Arial", 12), bg="#f8f9fa").pack(pady=10)

    tk.Label(payment_page, text="Name:", bg="#f8f9fa", font=("Arial", 12)).pack()
    name_entry = tk.Entry(payment_page, width=30)
    name_entry.pack(pady=5)

    tk.Label(payment_page, text="Phone Number:", bg="#f8f9fa", font=("Arial", 12)).pack()
    phone_entry = tk.Entry(payment_page, width=30)
    phone_entry.pack(pady=5)

    tk.Label(payment_page, text="Select Payment Method:", bg="#f8f9fa", font=("Arial", 12)).pack()
    payment_var = tk.StringVar()
    tk.Radiobutton(payment_page, text="UPI", variable=payment_var, value="UPI", bg="#f8f9fa").pack()
    tk.Radiobutton(payment_page, text="Card", variable=payment_var, value="Card", bg="#f8f9fa").pack()

    def confirm_payment():
        if not name_entry.get() or not phone_entry.get():
            messagebox.showerror("Error", "Please enter your name and phone number.")
            return
        if not payment_var.get():
            messagebox.showerror("Error", "Please select a payment method.")
            return

        token = random.randint(1000, 9999)
        save_billing_to_db(
            token=token,
            name=name_entry.get(),
            phone=phone_entry.get(),
            location=location_var.get(),
            vehicle_type=vehicle_type_var.get(),
            model=model_var.get(),
            duration=int(duration_var.get()),
            driver_required=driver_var.get(),
            base_cost=base_cost - gst,
            gst=gst,
            total_cost=total_cost
        )

        messagebox.showinfo("Payment Successful",
                            f"Your payment has been received!\nYour rental token: {token}\nPick up your car at the selected location.")
        open_billing_page(name_entry.get())

    tk.Button(payment_page, text="Pay Now", font=("Arial", 12), bg="#28a745", fg="white", command=confirm_payment).pack(pady=10)
    tk.Button(payment_page, text="Back", font=("Arial", 12), bg="#dc3545", fg="white", command=payment_page.destroy).pack(pady=5)

    footer_frame = tk.Frame(payment_page, bg="#ffc107", pady=10)
    footer_frame.pack(fill="x", side="bottom")
    tk.Label(footer_frame, text="© 2025 Car Rental Service", font=("Arial", 10), bg="#ffc107").pack()

tk.Button(root, text="About Us", font=("Arial", 12), bg="#17a2b8", fg="white", command=open_about_page).pack(pady=5)
tk.Button(root, text="Proceed to Payment", font=("Arial", 12), bg="#007bff", fg="white", command=open_payment_page).pack(pady=5)

root.mainloop()
 
