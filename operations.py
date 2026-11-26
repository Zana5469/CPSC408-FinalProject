import mysql.connector
from mysql.connector import Error

def connect_database():
    connection = mysql.connector.connect(
        host=
        port=
        user=
        password=
        database='bookstore'
    )

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


def get_filter_options():
    author_query = "SELECT DISTINCT AuthorName FROM author ORDER BY AuthorName;"
    genre_query = "SELECT DISTINCT Genre FROM book WHERE Genre is NOT NULL ORDER BY Genre;"
    book_query = "SELECT DISTINCT BookName FROM book ORDER BY BookName;"

    connection = connect_database()
    try:
        cursor = connection.cursor()
        try:
            cursor.execute(genre_query)
            genres = ["All"] + [row[0] for row in cursor]

            cursor.execute(author_query)
            authors = ["All"] + [row[0] for row in cursor]

            cursor.execute(book_query)
            books = ["All"] + [row[0] for row in cursor]

            return {
                "genres": genres,
                "authors": authors,
                "books": books,
            }
        finally:
            cursor.close()
    finally:
        connection.close()


def add_to_cart(buyerid, inventoryid, quantity):
    connection = connect_database()
    if connection is None:
        return False

    cursor = connection.cursor()

    try:
        # Check if the item is already in the cart
        check_query = """
            SELECT Quantity FROM cart
            WHERE BuyerID = %s AND InventoryID = %s;
        """
        cursor.execute(check_query, (buyerid, inventoryid))
        existing_item = cursor.fetchone()

        if existing_item:
            # Update the quantity of the existing item
            new_quantity = existing_item[0] + quantity
            update_query = """
                UPDATE cart
                SET Quantity = %s
                WHERE BuyerID = %s AND InventoryID = %s;
            """
            cursor.execute(update_query, (new_quantity, buyerid, inventoryid))
        else:
            # Insert a new item into the cart
            insert_query = """
                INSERT INTO cart (BuyerID, InventoryID, Quantity)
                VALUES (%s, %s, %s);
            """
            cursor.execute(insert_query, (buyerid, inventoryid, quantity))

        connection.commit()
        return True

    except Exception as error:
        print("Error adding to cart:", error)
        return False

    finally:
        cursor.close()
        connection.close()

