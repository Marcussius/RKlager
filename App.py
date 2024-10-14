import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

# Connect to SQLite database
conn = sqlite3.connect("inventory.db")
cursor = conn.cursor()

# Create the inventory table if it doesn't exist
def create_table():
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS inventory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_name TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        location TEXT NOT NULL,
        expiration_date TEXT,
        lot_number TEXT
    )
    """)
    conn.commit()

# Add new columns if they don't exist (Slet #)
# def alter_table():
#    try:
#        cursor.execute("ALTER TABLE inventory ADD COLUMN expiration_date TEXT")
#        cursor.execute("ALTER TABLE inventory ADD COLUMN lot_number TEXT")
#        conn.commit()
#    except sqlite3.OperationalError:
#        # Ignore if the column already exists
#        pass

#alter_table()  # Call this after connecting to the database

# Function to add an item
def add_item():
    item_name = entry_item.get()
    quantity = entry_quantity.get()
    location = entry_location.get()
    expiration_date = entry_expiration.get()
    lot_number = entry_lot.get()
    
    if item_name and quantity and location:
        cursor.execute("INSERT INTO inventory (item_name, quantity, location, expiration_date, lot_number) VALUES (?, ?, ?, ?, ?)",
                       (item_name, quantity, location, expiration_date, lot_number))
        conn.commit()
        messagebox.showinfo("Success", "Item added successfully!")
        clear_fields()
        display_items()
    else:
        messagebox.showerror("Error", "Please fill in all required fields!")

# Function to update an item
def update_item():
    item_id = entry_item_id.get()
    item_name = entry_item.get()
    quantity = entry_quantity.get()
    location = entry_location.get()
    expiration_date = entry_expiration.get()
    lot_number = entry_lot.get()

    if item_id:
        updates = []
        params = []
        if item_name:
            updates.append("item_name = ?")
            params.append(item_name)
        if quantity:
            updates.append("quantity = ?")
            params.append(quantity)
        if location:
            updates.append("location = ?")
            params.append(location)
        if expiration_date:
            updates.append("expiration_date = ?")
            params.append(expiration_date)
        if lot_number:
            updates.append("lot_number = ?")
            params.append(lot_number)
        
        if updates:
            query = f"UPDATE inventory SET {', '.join(updates)} WHERE id = ?"
            params.append(item_id)
            cursor.execute(query, tuple(params))
            conn.commit()
            messagebox.showinfo("Success", "Item updated successfully!")
            clear_fields()
            display_items()
        else:
            messagebox.showerror("Error", "No fields were provided for updating.")
    else:
        messagebox.showerror("Error", "Please provide the Item ID.")

# Function to delete an item
def delete_item():
    item_id = entry_item_id.get()
    
    if item_id:
        cursor.execute("DELETE FROM inventory WHERE id = ?", (item_id,))
        conn.commit()
        messagebox.showinfo("Success", "Item deleted successfully!")
        clear_fields()
        display_items()
    else:
        messagebox.showerror("Error", "Please provide the Item ID.")

# Function to search for an item by name or ID
def search_item():
    search_query = entry_search.get()
    
    if search_query:
        cursor.execute("SELECT * FROM inventory WHERE item_name LIKE ? OR id = ?", ('%' + search_query + '%', search_query))
        rows = cursor.fetchall()
        update_treeview(rows)
    else:
        messagebox.showerror("Error", "Please enter a search term.")

# Function to display all items
def display_items():
    cursor.execute("SELECT * FROM inventory")
    rows = cursor.fetchall()
    update_treeview(rows)

# Function to add to quantity
def add_quantity():
    item_id = entry_item_id.get()
    add_amount = entry_quantity.get()

    if item_id and add_amount:
        cursor.execute("SELECT quantity FROM inventory WHERE id = ?", (item_id,))
        current_quantity = cursor.fetchone()[0]
        
        new_quantity = int(current_quantity) + int(add_amount)
        cursor.execute("UPDATE inventory SET quantity = ? WHERE id = ?", (new_quantity, item_id))
        conn.commit()
        messagebox.showinfo("Success", "Quantity updated successfully!")
        clear_fields()
        display_items()
    else:
        messagebox.showerror("Error", "Please provide Item ID and quantity.")

# Function to subtract from quantity
def remove_quantity():
    item_id = entry_item_id.get()
    remove_amount = entry_quantity.get()

    if item_id and remove_amount:
        cursor.execute("SELECT quantity FROM inventory WHERE id = ?", (item_id,))
        current_quantity = cursor.fetchone()[0]
        
        new_quantity = int(current_quantity) - int(remove_amount)
        if new_quantity < 0:
            new_quantity = 0
        
        cursor.execute("UPDATE inventory SET quantity = ? WHERE id = ?", (new_quantity, item_id))
        conn.commit()
        messagebox.showinfo("Success", "Quantity updated successfully!")
        clear_fields()
        display_items()
    else:
        messagebox.showerror("Error", "Please provide Item ID and quantity.")

# Update the treeview with inventory data
def update_treeview(rows):
    for row in tree.get_children():
        tree.delete(row)
    for row in rows:
        tree.insert("", "end", values=row)

# Function to auto-fill fields when an item is double-clicked
def on_item_double_click(event):
    selected_item = tree.selection()[0]
    item_data = tree.item(selected_item)['values']

    entry_item_id.delete(0, tk.END)
    entry_item_id.insert(0, item_data[0])

    entry_item.delete(0, tk.END)
    entry_item.insert(0, item_data[1])

    entry_quantity.delete(0, tk.END)
    entry_quantity.insert(0, item_data[2])

    entry_location.delete(0, tk.END)
    entry_location.insert(0, item_data[3])

    entry_expiration.delete(0, tk.END)
    entry_expiration.insert(0, item_data[4])

    entry_lot.delete(0, tk.END)
    entry_lot.insert(0, item_data[5])

# Function to clear input fields
def clear_fields():
    entry_item_id.delete(0, tk.END)
    entry_item.delete(0, tk.END)
    entry_quantity.delete(0, tk.END)
    entry_location.delete(0, tk.END)
    entry_expiration.delete(0, tk.END)
    entry_lot.delete(0, tk.END)
    entry_item.focus()

# GUI setup
root = tk.Tk()
root.title("Inventory Management System")

# Configure the root window for resizing
root.grid_rowconfigure(2, weight=1)  # Row 2 will stretch (Treeview section)
root.grid_columnconfigure(0, weight=1)

frame_search = tk.Frame(root)
frame_search.grid(row=0, column=0, sticky="ew", padx=10, pady=10)

# Search Field
tk.Label(frame_search, text="Search Item/ID:").pack(side=tk.LEFT)
entry_search = tk.Entry(frame_search)
entry_search.pack(side=tk.LEFT)
btn_search = tk.Button(frame_search, text="Search Item", command=search_item)
btn_search.pack(side=tk.LEFT)

frame = tk.Frame(root)
frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

# Item Name
tk.Label(frame, text="Item Name:").grid(row=0, column=0)
entry_item = tk.Entry(frame)
entry_item.grid(row=0, column=1)

# Quantity
tk.Label(frame, text="Quantity:").grid(row=1, column=0)
entry_quantity = tk.Entry(frame)
entry_quantity.grid(row=1, column=1)

# Location
tk.Label(frame, text="Location:").grid(row=2, column=0)
entry_location = tk.Entry(frame)
entry_location.grid(row=2, column=1)

# Expiration Date
tk.Label(frame, text="Expiration Date:").grid(row=3, column=0)
entry_expiration = tk.Entry(frame)
entry_expiration.grid(row=3, column=1)

# Lot Number
tk.Label(frame, text="Lot Number:").grid(row=4, column=0)
entry_lot = tk.Entry(frame)
entry_lot.grid(row=4, column=1)

# Item ID for updating/deleting
tk.Label(frame, text="Item ID:").grid(row=5, column=0)
entry_item_id = tk.Entry(frame)
entry_item_id.grid(row=5, column=1)

# Add Button
btn_add = tk.Button(frame, text="Add Item", command=add_item)
btn_add.grid(row=6, column=0, pady=5)

# Update Button
btn_update = tk.Button(frame, text="Update Item", command=update_item)
btn_update.grid(row=6, column=1, pady=5)

# Delete Button
btn_delete = tk.Button(frame, text="Delete Item", command=delete_item)
btn_delete.grid(row=6, column=2, pady=5)

# Add and Remove Quantity Buttons
btn_add_quantity = tk.Button(frame, text="Add", command=add_quantity)
btn_add_quantity.grid(row=1, column=2)
btn_remove_quantity = tk.Button(frame, text="Remove", command=remove_quantity)
btn_remove_quantity.grid(row=1, column=3)

# Treeview to display inventory
tree_frame = tk.Frame(root)
tree_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")

tree_scroll_y = tk.Scrollbar(tree_frame, orient=tk.VERTICAL)
tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

tree_scroll_x = tk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
tree_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

tree = ttk.Treeview(tree_frame, yscrollcommand=tree_scroll_y.set, xscrollcommand=tree_scroll_x.set, columns=("ID", "Item", "Quantity", "Location", "Expiration Date", "Lot Number"), show="headings")
tree.pack(fill="both", expand=True)

tree_scroll_y.config(command=tree.yview)
tree_scroll_x.config(command=tree.xview)

tree.heading("ID", text="ID")
tree.heading("Item", text="Item")
tree.heading("Quantity", text="Quantity")
tree.heading("Location", text="Location")
tree.heading("Expiration Date", text="Expiration Date")
tree.heading("Lot Number", text="Lot Number")

# Double-click to auto-fill item data
tree.bind("<Double-1>", on_item_double_click)

# Display items when the app starts
create_table()
display_items()

root.mainloop()
