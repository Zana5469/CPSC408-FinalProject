CREATE DATABASE bookstore;

CREATE TABLE author (
	AuthorID INT PRIMARY KEY AUTO_INCREMENT,
	AuthorName VARCHAR (30) NOT NULL,
	DOB DATE,
	Gender VARCHAR (10),
	NetWorth FLOAT,
	Nationality VARCHAR (20)
);

CREATE TABLE book (
	BookID INT PRIMARY KEY AUTO_INCREMENT,
	BookName VARCHAR(50) NOT NULL,
	AuthorID INT NOT NULL,
	FOREIGN KEY (AuthorID) REFERENCES author(AuthorID),
	Genre VARCHAR(15),
	Publisher VARCHAR(30),
	ReleaseDate DATE NOT NULL
);

CREATE TABLE store (
	StoreID INT PRIMARY KEY AUTO_INCREMENT,
	StoreName VARCHAR(30) NOT NULL,
	PhoneNumber VARCHAR(15) NOT NULL,
	Location VARCHAR(200) NOT NULL,
	OpenTime TIME,
	CloseTime TIME,
	DaysOpen VARCHAR(40)
);

CREATE TABLE buyer (
	BuyerID INT PRIMARY KEY AUTO_INCREMENT,
	BuyerName VARCHAR(30) NOT NULL,
	PhoneNumber VARCHAR(15) NOT NULL,
	Address VARCHAR(50) NOT NULL,
	PaymentMethod VARCHAR(10) NOT NULL
);

CREATE TABLE inventory (
	InventoryID INT PRIMARY KEY AUTO_INCREMENT,
	BookID INT NOT NULL,
	FOREIGN KEY (BookID) REFERENCES book(BookID),
	StoreID INT NOT NULL,
	FOREIGN KEY (StoreID) REFERENCES store(StoreID),
	Price FLOAT NOT NULL,
	Quantity INT NOT NULL
);

CREATE TABLE orders (
	OrderID INT PRIMARY KEY AUTO_INCREMENT,
	BookID INT NOT NULL,
	FOREIGN KEY (BookID) REFERENCES book(BookID),
	StoreID INT NOT NULL,
	FOREIGN KEY (StoreID) REFERENCES store(StoreID),
	BuyerID INT NOT NULL,
	FOREIGN KEY (BuyerID) REFERENCES buyer(BuyerID),
	BookQuantity INT NOT NULL
);

CREATE TABLE cart (
	CartID INT PRIMARY KEY AUTO_INCREMENT,
	InventoryID INT NOT NULL,
	FOREIGN KEY (InventoryID) REFERENCES inventory(InventoryID),
	BuyerID INT NOT NULL,
	FOREIGN KEY (BuyerID) REFERENCES buyer(BuyerID),
	StoreID INT NOT NULL,
	FOREIGN KEY (StoreID) REFERENCES store(StoreID),
	BookQuantity INT NOT NULL
);

-- 1. Authors
INSERT INTO author (AuthorName, DOB, Gender, NetWorth, Nationality) VALUES
('George Orwell', '1903-06-25', 'Male', 1000000.00, 'British'),
('Jane Austen', '1775-12-16', 'Female', 2500000.00, 'British'),
('Haruki Murakami', '1949-01-12', 'Male', 50000000.00, 'Japanese'),
('Octavia E. Butler', '1947-06-22', 'Female', 3500000.00, 'American'),
('Gabriel Garcia Marquez', '1927-03-06', 'Male', 40000000.00, 'Colombian'),
('Agatha Christie', '1890-09-15', 'Female', 600000000.00, 'British');

-- 2. Books
INSERT INTO book (BookName, AuthorID, Genre, Publisher, ReleaseDate) VALUES
('1984', 1, 'Sci-Fi', 'Secker & Warburg', '1949-06-08'),
('Animal Farm', 1, 'Satire', 'Secker & Warburg', '1945-08-17'),
('Pride and Prejudice', 2, 'Romance', 'T. Egerton', '1813-01-28'),
('Kafka on the Shore', 3, 'Fantasy', 'Shinchosha', '2002-09-12'),
('Norwegian Wood', 3, 'Fiction', 'Kodansha', '1987-09-04'),
('Kindred', 4, 'Sci-Fi', 'Doubleday', '1979-06-01'),
('One Hundred Years of Solitude', 5, 'Magic Realism', 'Harper & Row', '1967-05-30'),
('Murder on the Orient Express', 6, 'Mystery', 'Collins Crime Club', '1934-01-01');

-- 3. Stores
INSERT INTO store (StoreName, PhoneNumber, Location, OpenTime, CloseTime, DaysOpen) VALUES
('City Lights Books', '415-555-0101', '261 Columbus Ave, San Francisco, CA', '10:00:00', '22:00:00', 'Mon-Sun'),
('Powell''s City of Books', '503-555-0142', '1005 W Burnside St, Portland, OR', '09:00:00', '21:00:00', 'Mon-Sun'),
('Strand Bookstore', '212-555-0188', '828 Broadway, New York, NY', '10:00:00', '20:00:00', 'Mon-Sat'),
('The Last Bookstore', '213-555-0199', '453 S Spring St, Los Angeles, CA', '11:00:00', '20:00:00', 'Tue-Sun');

-- 4. Buyers
INSERT INTO buyer (BuyerName, PhoneNumber, Address, PaymentMethod) VALUES
('Alice Johnson', '415-555-0211', '742 Evergreen Ter, San Francisco, CA', 'Credit'),
('Marcus Vance', '503-555-0222', '128 NW Couch St, Portland, OR', 'Debit'),
('Elena Rostova', '212-555-0233', '450 W 33rd St, New York, NY', 'PayPal'),
('David Kim', '213-555-0244', '910 S Broadway, Los Angeles, CA', 'Apple Pay'),
('Sofia Martinez', '619-555-0255', '305 Harbor Dr, San Diego, CA', 'Cash');

-- 5. Inventory
INSERT INTO inventory (BookID, StoreID, Price, Quantity) VALUES
(1, 1, 15.99, 25),
(2, 1, 12.50, 18),
(3, 2, 14.00, 30),
(4, 2, 18.99, 12),
(5, 3, 16.50, 20),
(6, 3, 17.25, 15),
(7, 4, 19.99, 10),
(8, 4, 13.75, 22),
(1, 3, 16.00, 14),
(4, 1, 18.50, 9);

-- 6. Orders
INSERT INTO orders (BookID, StoreID, BuyerID, BookQuantity) VALUES
(1, 1, 1, 2),
(3, 2, 2, 1),
(5, 3, 3, 3),
(7, 4, 4, 1),
(8, 4, 5, 2),
(4, 1, 1, 1);

-- 7. Cart (StoreID matches the StoreID of the referenced InventoryID)
INSERT INTO cart (InventoryID, BuyerID, StoreID, BookQuantity) VALUES
(2, 1, 1, 1),
(4, 2, 2, 2),
(6, 3, 3, 1),
(7, 4, 4, 1),
(9, 5, 3, 2);
