USE ardenleaf;

-- Clean existing data
SET FOREIGN_KEY_CHECKS = 0;
TRUNCATE TABLE Bookmark;
TRUNCATE TABLE Loan;
TRUNCATE TABLE BookCopy;
TRUNCATE TABLE Bookstore;
TRUNCATE TABLE Library;
TRUNCATE TABLE Book_Genre;
TRUNCATE TABLE Book_Author;
TRUNCATE TABLE Book;
TRUNCATE TABLE Author;
TRUNCATE TABLE Publisher;
TRUNCATE TABLE Customer;
TRUNCATE TABLE Member;
TRUNCATE TABLE User_Phone;
TRUNCATE TABLE User;
SET FOREIGN_KEY_CHECKS = 1;

-- Users
INSERT INTO User (Name, Email, PasswordHash, UserType) VALUES
('Alice Smith',   'alice@example.com',   'scrypt:32768:8:1$K4GpO1WgtGzyL9Zd$958520cae2825b7a141314e47237e540488fffaed28369e44a8c1ec6eaa710b5d71d8ce91a310224ed3162de5d8482102901f495cb41323df8cde654abf69e65', 'Member'),
('Bob Johnson',   'bob@example.com',     'scrypt:32768:8:1$BSpYehIKl5SIvP4v$90d6454a24d0606ad0cd7648155ca53dfa60b64363613abe19cc38d4c9d86ad63b35801e920fca4cda4e2d7126870b08de7992a0c7d1eb0b5d5e4084e26d2d53', 'Member'),
('Charlie Brown', 'charlie@example.com', 'scrypt:32768:8:1$N01LACki46kFQ4Eh$95bb2d7e3e590cf852438811ee128953b14067d7d8730957a3d554f21f31583b5f2afa12c426b3adf807a312f24930a694a5ddca726da571b3e060a0ddaa7105', 'Customer'),
('Diana Prince',  'diana@example.com',   'scrypt:32768:8:1$LCOIHIJhRmHyY0qv$32c6fb093c8751b1761ffb63b27159124a55ca70a2c068760c1b17c7562e3aea29f82c7eb7dd019338a32f445f47d12f3ad5e896ce59cdbbecbe85113c06cbd9', 'Customer');

-- Determine explicit UserIDs (Assuming 1 to 4 because of truncate/auto-inc reset usually doesn't happen with DELETE, so let's insert explicitly)
-- Wait, TRUNCATE resets AUTO_INCREMENT. So UserIDs are 1(Alice), 2(Bob), 3(Charlie), 4(Diana)

-- Specializations
INSERT INTO Member (UserID, MembershipDate, MaxBooks) VALUES
(1, '2023-01-15', 5),
(2, '2023-06-20', 5);

INSERT INTO Customer (UserID, LoyaltyPoints) VALUES
(3, 120),
(4, 300);

-- User Phones
INSERT INTO User_Phone (Phone, UserID) VALUES
('555-0101', 1),
('555-0102', 1),
('555-0201', 2),
('555-0301', 3);

-- Publishers
INSERT INTO Publisher (Name, Address) VALUES
('Penguin Random House', 'New York, USA'),
('HarperCollins', 'London, UK'),
('Scholastic', 'New York, USA'),
('Scribner', 'Jersey City, USA');

-- Authors
INSERT INTO Author (Name) VALUES
('J.K. Rowling'),
('George R.R. Martin'),
('Isaac Asimov'),
('Agatha Christie'),
('Suzanne Collins'),
('Paulo Coelho'),
('James Clear'),
('F. Scott Fitzgerald'),
('Yuval Noah Harari');

-- Books
INSERT INTO Book (ISBN, Title, PublisherID, PublicationYear) VALUES
('978-0439708180', 'Harry Potter and the Sorceler''s Stone', 1, 1997),
('978-0553103540', 'A Game of Thrones', 2, 1996),
('978-0553293357', 'Foundation', 1, 1951),
('978-0062073488', 'And Then There Were None', 2, 1939),
('9780439023481', 'The Hunger Games', 3, 2008),
('9780062315007', 'The Alchemist', 2, 1988),
('9780735211292', 'Atomic Habits', 1, 2018),
('9780743273565', 'The Great Gatsby', 4, 1925),
('9780062316110', 'Sapiens', 2, 2011);

-- Book_Author
INSERT INTO Book_Author (ISBN, AuthorID) VALUES
('978-0439708180', 1),
('978-0553103540', 2),
('978-0553293357', 3),
('978-0062073488', 4),
('9780439023481', 5),
('9780062315007', 6),
('9780735211292', 7),
('9780743273565', 8),
('9780062316110', 9);

-- Book_Genre
INSERT INTO Book_Genre (ISBN, Genre) VALUES
('978-0439708180', 'Fantasy'),
('978-0439708180', 'Young Adult'),
('978-0553103540', 'Fantasy'),
('978-0553103540', 'Political Drama'),
('978-0553293357', 'Science Fiction'),
('978-0062073488', 'Mystery'),
('978-0062073488', 'Thriller'),
('9780439023481', 'Dystopian'),
('9780439023481', 'Young Adult'),
('9780062315007', 'Fiction'),
('9780062315007', 'Philosophy'),
('9780735211292', 'Self-help'),
('9780735211292', 'Productivity'),
('9780743273565', 'Classic'),
('9780743273565', 'Fiction'),
('9780062316110', 'History'),
('9780062316110', 'Non-Fiction');

-- Library & Bookstore
INSERT INTO Library (Name, Location) VALUES
('Central City Library', 'Downtown Avenue, City Center'),
('Westside Branch', 'West End, City Outer');

INSERT INTO Bookstore (Name, Location) VALUES
('Chapters & Pages', 'Mall Boulevard'),
('The Reading Corner', 'North Street');

-- Book Copies (Mix of library and bookstore inventories)
-- Library copies: Price and DiscountPercent are NULL
-- Bookstore copies: Price and optional DiscountPercent are set
INSERT INTO BookCopy (ISBN, LibraryID, StoreID, Status, Price, DiscountPercent) VALUES
('978-0439708180', 1, NULL, 'Available', NULL, NULL),   -- Harry Potter (Lib 1)
('978-0439708180', 1, NULL, 'Borrowed',  NULL, NULL),   -- Harry Potter (Lib 1 - Out)
('978-0553103540', 2, NULL, 'Available', NULL, NULL),   -- Game of Thrones (Lib 2)
('978-0553293357', NULL, 1, 'Sold',      499.00, 10),   -- Foundation (Sold)
('978-0553293357', NULL, 1, 'Available', 499.00, NULL), -- Foundation (Store 1)
('978-0062073488', NULL, 2, 'Available', 349.00, 15),   -- And Then There Were None (Store 2)

-- The Hunger Games
('9780439023481', 1, NULL, 'Available', NULL, NULL),
('9780439023481', 2, NULL, 'Available', NULL, NULL),
('9780439023481', NULL, 1, 'Available', 399.00, 10),

-- The Alchemist
('9780062315007', 1, NULL, 'Available', NULL, NULL),
('9780062315007', 2, NULL, 'Available', NULL, NULL),
('9780062315007', NULL, 1, 'Available', 299.00, NULL),

-- Atomic Habits
('9780735211292', 1, NULL, 'Available', NULL, NULL),
('9780735211292', 2, NULL, 'Available', NULL, NULL),
('9780735211292', NULL, 1, 'Available', 450.00, 5),

-- The Great Gatsby
('9780743273565', 1, NULL, 'Available', NULL, NULL),
('9780743273565', 2, NULL, 'Available', NULL, NULL),
('9780743273565', NULL, 1, 'Available', 250.00, NULL),

-- Sapiens
('9780062316110', 1, NULL, 'Available', NULL, NULL),
('9780062316110', 2, NULL, 'Available', NULL, NULL),
('9780062316110', NULL, 1, 'Available', 550.00, 15);

-- Loans (Only for Members borrowing from Library)
-- CopyID 2 is assumed to be the 'Borrowed' Harry Potter (since it's the 2nd one inserted)
INSERT INTO Loan (CopyID, MemberID, IssueDate, DueDate, ReturnDate) VALUES
(2, 1, DATE_SUB(CURDATE(), INTERVAL 20 DAY), DATE_SUB(CURDATE(), INTERVAL 6 DAY), NULL), -- Overdue by 6 days
(1, 2, DATE_SUB(CURDATE(), INTERVAL 30 DAY), DATE_SUB(CURDATE(), INTERVAL 16 DAY), DATE_SUB(CURDATE(), INTERVAL 10 DAY)); -- Was overdue by 6 days when returned

-- Bookmarks (Users saving books for later)
-- Alice (UserID=1) bookmarks Game of Thrones and Foundation
-- Bob (UserID=2) bookmarks Harry Potter
-- Charlie (UserID=3, Customer) bookmarks And Then There Were None
INSERT INTO Bookmark (UserID, ISBN) VALUES
(1, '978-0553103540'),
(1, '978-0553293357'),
(2, '978-0439708180'),
(3, '978-0062073488');
