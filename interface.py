import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector


# DATABASE CONNECTION
def connect_database():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="CPSC408",
        database="bookstore"
    )

# MAIN WINDOW
root = tk.Tk()
root.title("Bookstore")
root.geometry("1000x650")
root.configure(bg="#F5F0E8")

# HEADER
header = tk.Frame(root, bg="#ACE2B0",height=80)
header.pack(fill="x")

title = tk.Label(
    header,
    text="GIRARD'S BOOKSTORE",
    font=("Georgia", 24, "bold"),
    fg="DARKGREEN",
    bg="#ACE2B0"
)
title.pack(pady=20)

# SEARCH SECTION
search_frame = tk.Frame(root, bg="#F5F0E8")
search_frame.pack(fill="x", padx=20, pady=15)

tk.Label(
    search_frame,
    text="Search books:",
    font=("Arial", 12),
    bg="#F5F0E8",
    fg="black",
).pack(side="left")

search_entry = tk.Entry(search_frame, width=35, font=("Arial", 12))
search_entry.pack(side="left", padx=10)


# BOOK CATALOG
catalog_frame = tk.Frame(root, bg="#F5F0E8")
catalog_frame.pack(fill="both", expand=True, padx=20)

columns = (
    "InventoryID",
    "BookName",
    "AuthorName",
    "Genre",
    "StoreName",
    "Price",
    "Quantity"
)

book_table = ttk.Treeview(
    catalog_frame,
    columns=columns,
    show="headings"
)

book_table.heading("InventoryID", text="Inventory ID")
book_table.heading("BookName", text="Book Title")
book_table.heading("AuthorName", text="Author")
book_table.heading("Genre", text="Genre")
book_table.heading("StoreName", text="Store")
book_table.heading("Price", text="Price")
book_table.heading("Quantity", text="Stock")

book_table.column("InventoryID", width=80)
book_table.column("BookName", width=180)
book_table.column("AuthorName", width=150)
book_table.column("Genre", width=100)
book_table.column("StoreName", width=150)
book_table.column("Price", width=80)
book_table.column("Quantity", width=70)

book_table.pack(fill="both", expand=True)


# LOAD BOOKS FROM MYSQL

def load_books(search_text=""):

    try:
        connection = connect_database()
        cursor = connection.cursor()

        query = """
            SELECT
                i.InventoryID,
                b.BookName,
                a.AuthorName,
                b.Genre,
                s.StoreName,
                i.Price,
                i.Quantity
            FROM inventory i
            JOIN book b
                ON i.BookID = b.BookID
            JOIN author a
                ON b.AuthorID = a.AuthorID
            JOIN store s
                ON i.StoreID = s.StoreID
            WHERE b.BookName LIKE %s
               OR a.AuthorName LIKE %s
            ORDER BY b.BookName
        """

        search = "%" + search_text + "%"

        cursor.execute(query, (search, search))

        results = cursor.fetchall()

        # Clear old results
        for row in book_table.get_children():
            book_table.delete(row)

        # Display new results
        for row in results:
            book_table.insert("", "end", values=row)

        cursor.close()
        connection.close()

    except mysql.connector.Error as error:
        messagebox.showerror(
            "Database Error",
            str(error)
        )


# SEARCH BUTTON
def search_books(search_text):
    connection = connect_database()

    if connection is None:
        return []

    cursor = connection.cursor()

    search_text = search_text.strip()
    search_pattern = f"%{search_text}%"

    query = """
        SELECT
            b.BookID,
            b.BookName,
            a.AuthorName,
            b.Genre,
            b.Publisher,
            i.Price,
            i.Quantity,
            s.StoreName
        FROM book b
        JOIN author a
            ON b.AuthorID = a.AuthorID
        JOIN inventory i
            ON b.BookID = i.BookID
        JOIN store s
            ON i.StoreID = s.StoreID
        WHERE
            b.BookName LIKE %s
            OR a.AuthorName LIKE %s
            OR b.Genre LIKE %s
            OR b.Publisher LIKE %s
        ORDER BY b.BookName;
    """

    try:
        cursor.execute(
            query,
            (
                search_pattern,
                search_pattern,
                search_pattern,
                search_pattern
            )
        )

        results = cursor.fetchall()
        return results

    except Exception as error:
        print("Search error:", error)
        return []

    finally:
        cursor.close()
        connection.close()

search_button = tk.Button(
    search_frame,
    text="Search",
    command=search_books,
    bg="#8B5E3C",
    fg="black",
    font=("Arial", 11)
)

search_button.pack(side="left")

quit_button = ttk.Button(
    root,
    text="Quit",
    command=root.destroy
)
quit_button.pack(side="right")

# ADD TO CART

cart_frame = tk.Frame(root, bg="#F5F0E8")
cart_frame.pack(fill="x", padx=20, pady=15)

tk.Label(
    cart_frame,
    text="Buyer ID:",
    bg="#F5F0E8",
    fg="black"
).pack(side="left")

buyer_entry = tk.Entry(cart_frame, width=10)
buyer_entry.pack(side="left", padx=5)

tk.Label(
    cart_frame,
    text="Quantity:",
    bg="#F5F0E8", 
    fg = "black"
).pack(side="left", padx=10)

quantity_entry = tk.Entry(cart_frame, width=10)
quantity_entry.insert(0, "1")
quantity_entry.pack(side="left", padx=5)


def add_to_cart():

    selected = book_table.selection()

    if not selected:
        messagebox.showwarning(
            "Select a Book",
            "Please select a book first."
        )
        return

    try:
        buyer_id = int(buyer_entry.get())
        quantity = int(quantity_entry.get())

        if buyer_id <= 0 or quantity <= 0:
            raise ValueError

    except ValueError:
        messagebox.showerror(
            "Invalid Input",
            "Enter a valid buyer ID and quantity."
        )
        return

    # Get selected book information
    book_values = book_table.item(
        selected[0], "values"
    )

    inventory_id = int(book_values[0])
    store_id = None
    available_quantity = int(book_values[6])

    if quantity > available_quantity:
        messagebox.showerror(
            "Insufficient Stock",
            "Not enough books available."
        )
        return

    try:
        connection = connect_database()
        cursor = connection.cursor()

        # Retrieve StoreID for selected inventory
        cursor.execute(
            """
            SELECT StoreID
            FROM inventory
            WHERE InventoryID = %s
            """,
            (inventory_id,)
        )

        result = cursor.fetchone()

        if result is None:
            raise ValueError("Inventory item not found.")

        store_id = result[0]

        # Check that buyer exists
        cursor.execute(
            """
            SELECT BuyerID
            FROM buyer
            WHERE BuyerID = %s
            """,
            (buyer_id,)
        )

        if cursor.fetchone() is None:
            raise ValueError("Buyer ID does not exist.")

        # Insert item into cart
        cursor.execute(
            """
            INSERT INTO cart
                (InventoryID, BuyerID, StoreID, BookQuantity)
            VALUES (%s, %s, %s, %s)
            """,
            (
                inventory_id,
                buyer_id,
                store_id,
                quantity
            )
        )

        connection.commit()

        messagebox.showinfo(
            "Success",
            "Book added to cart!"
        )

        cursor.close()
        connection.close()

    except (mysql.connector.Error, ValueError) as error:
        messagebox.showerror(
            "Error",
            str(error)
        )


add_cart_button = tk.Button(
    cart_frame,
    text="Add to Cart",
    command=add_to_cart,
    bg="#4B3025",
    fg="black",
    font=("Arial", 11)
)

add_cart_button.pack(side="left", padx=15)


# START APPLICATION

load_books()
root.mainloop()

#destructor 
ttk.Button(root, text="Quit", command=root.destroy).grid(column=1, row=0)