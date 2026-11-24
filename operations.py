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
