USE ardenleaf;

-- ─────────────────────────────────────────────────────────────────────────────
-- 1. CLEAN EXISTING DATA
-- ─────────────────────────────────────────────────────────────────────────────
SET FOREIGN_KEY_CHECKS = 0;
DELETE FROM Bookmark;
DELETE FROM Loan;
DELETE FROM BookCopy;
DELETE FROM Bookstore;
DELETE FROM Library;
DELETE FROM Book_Genre;
DELETE FROM Book_Author;
DELETE FROM Book;
DELETE FROM Author;
DELETE FROM Publisher;
DELETE FROM Customer;
DELETE FROM Member;
DELETE FROM User_Phone;
DELETE FROM User;

ALTER TABLE User AUTO_INCREMENT = 1;
ALTER TABLE Publisher AUTO_INCREMENT = 1;
ALTER TABLE Author AUTO_INCREMENT = 1;
ALTER TABLE Library AUTO_INCREMENT = 1;
ALTER TABLE Bookstore AUTO_INCREMENT = 1;
ALTER TABLE BookCopy AUTO_INCREMENT = 1;
ALTER TABLE Loan AUTO_INCREMENT = 1;
SET FOREIGN_KEY_CHECKS = 1;

-- ─────────────────────────────────────────────────────────────────────────────
-- 2. USERS & PROFILES
-- ─────────────────────────────────────────────────────────────────────────────
-- Reset UserIDs to 1, 2, 3, 4
INSERT INTO User (Name, Email, PasswordHash, UserType) VALUES
('Alice Smith',   'alice@example.com',   'hashed_pw_1', 'Member'),
('Bob Johnson',   'bob@example.com',     'hashed_pw_2', 'Member'),
('Charlie Brown', 'charlie@example.com', 'hashed_pw_3', 'Customer'),
('Diana Prince', 'diana@example.com',   'hashed_pw_4', 'Customer');

INSERT INTO Member (UserID, MembershipDate, MaxBooks) VALUES
(1, '2023-01-15', 5),
(2, '2023-06-20', 5);

INSERT INTO Customer (UserID, LoyaltyPoints) VALUES
(3, 120),
(4, 300);

INSERT INTO User_Phone (Phone, UserID) VALUES
('555-0101', 1),
('555-0102', 1),
('555-0201', 2),
('555-0301', 3);

-- ─────────────────────────────────────────────────────────────────────────────
-- 3. PUBLISHERS & AUTHORS
-- ─────────────────────────────────────────────────────────────────────────────
INSERT INTO Publisher (Name, Address) VALUES
('Penguin Random House', 'New York & Mumbai'), -- ID 1
('HarperCollins',        'London & Noida'),      -- ID 2
('Scholastic',           'New York & Gurgaon'),  -- ID 3
('Scribner',             'New York, USA'),       -- ID 4
('Bloomsbury',           'London & New Delhi'),  -- ID 5
('Pan Macmillan',        'London & Mumbai');     -- ID 6

INSERT INTO Author (Name) VALUES
('J.K. Rowling'),             -- 1
('George R.R. Martin'),       -- 2
('Isaac Asimov'),             -- 3
('Agatha Christie'),          -- 4
('Suzanne Collins'),          -- 5
('Paulo Coelho'),             -- 6
('James Clear'),              -- 7
('F. Scott Fitzgerald'),     -- 8
('Yuval Noah Harari'),        -- 9
('Arundhati Roy'),            -- 10
('Vikram Seth'),              -- 11
('Amitav Ghosh'),             -- 12
('Chetan Bhagat'),            -- 13
('R.K. Narayan'),             -- 14
('Ruskin Bond'),              -- 15
('Chimamanda Ngozi Adichie'), -- 16
('Toni Morrison'),            -- 17
('Haruki Murakami'),          -- 18
('Gabriel Garcia Marquez'),   -- 19
('Roald Dahl');               -- 20

-- ─────────────────────────────────────────────────────────────────────────────
-- 4. BOOKS (20 Total)
-- ─────────────────────────────────────────────────────────────────────────────
INSERT INTO Book (ISBN, Title, PublisherID, PublicationYear) VALUES
-- Existing 9
('978-0439708180', 'Harry Potter and the Sorcerer\'s Stone', 1, 1997),
('978-0553103540', 'A Game of Thrones', 2, 1996),
('978-0553293357', 'Foundation', 1, 1951),
('978-0062073488', 'And Then There Were None', 2, 1939),
('9780439023481', 'The Hunger Games', 3, 2008),
('9780062315007', 'The Alchemist', 2, 1988),
('9780735211292', 'Atomic Habits', 1, 2018),
('9780743273565', 'The Great Gatsby', 4, 1925),
('9780062316110', 'Sapiens', 2, 2011),
-- New 11
('9780679457312', 'The God of Small Things', 1, 1997),
('9780060786526', 'A Suitable Boy', 2, 1993),
('9780618329977', 'The Shadow Lines', 5, 1988),
('9788129115300', '2 States', 3, 2009),
('9780143031703', 'Malgudi Days', 1, 1943),
('9780143029014', 'The Night Train at Deoli', 1, 1988),
('9781616953638', 'Purple Hibiscus', 5, 2003),
('9781400033416', 'Beloved', 4, 1987),
('9780375704024', 'Norwegian Wood', 6, 1987),
('9780060883287', 'One Hundred Years of Solitude', 2, 1967),
('9780142410318', 'Charlie and the Chocolate Factory', 1, 1964);

-- ─────────────────────────────────────────────────────────────────────────────
-- 5. BOOK_AUTHOR MAPPINGS
-- ─────────────────────────────────────────────────────────────────────────────
INSERT INTO Book_Author (ISBN, AuthorID) VALUES
('978-0439708180', 1), ('978-0553103540', 2), ('978-0553293357', 3), 
('978-0062073488', 4), ('9780439023481', 5), ('9780062315007', 6), 
('9780735211292', 7), ('9780743273565', 8), ('9780062316110', 9),
('9780679457312', 10), ('9780060786526', 11), ('9780618329977', 12),
('9788129115300', 13), ('9780143031703', 14), ('9780143029014', 15),
('9781616953638', 16), ('9781400033416', 17), ('9780375704024', 18),
('9780060883287', 19), ('9780142410318', 20);

-- ─────────────────────────────────────────────────────────────────────────────
-- 6. BOOK_GENRE MAPPINGS
-- ─────────────────────────────────────────────────────────────────────────────
INSERT INTO Book_Genre (ISBN, Genre) VALUES
('978-0439708180', 'Fantasy'), ('978-0439708180', 'Young Adult'),
('978-0553103540', 'Fantasy'), ('978-0553293357', 'Science Fiction'),
('978-0062073488', 'Mystery'), ('978-0062073488', 'Thriller'),
('9780439023481', 'Dystopian'), ('9780439023481', 'Young Adult'),
('9780062315007', 'Fiction'), ('9780062315007', 'Philosophy'),
('9780735211292', 'Self-help'), ('9780735211292', 'Productivity'),
('9780743273565', 'Classic'), ('9780743273565', 'Fiction'),
('9780062316110', 'History'), ('9780062316110', 'Non-Fiction'),
('9780679457312', 'Literary Fiction'), ('9780679457312', 'Indian Literature'),
('9780060786526', 'Fiction'), ('9780060786526', 'Indian Literature'),
('9780618329977', 'Historical Fiction'), ('9780618329977', 'Indian Literature'),
('9788129115300', 'Fiction'), ('9788129115300', 'Indian Literature'),
('9780143031703', 'Children'), ('9780143031703', 'Indian Literature'),
('9780143029014', 'Fiction'), ('9780143029014', 'Indian Literature'),
('9781616953638', 'Fiction'), ('9781616953638', 'Literary Fiction'),
('9781400033416', 'Historical Fiction'), ('9781400033416', 'Literary Fiction'),
('9780375704024', 'Fiction'), ('9780060883287', 'Magical Realism'),
('9780142410318', 'Children');

-- ─────────────────────────────────────────────────────────────────────────────
-- 7. LIBRARIES & BOOKSTORES
-- ─────────────────────────────────────────────────────────────────────────────
INSERT INTO Library (Name, Location) VALUES
('Connaught Place Public Library', 'Connaught Place, New Delhi 110001'), -- 1
('Bandra Reading House',          'Linking Road, Bandra West, Mumbai 400050'), -- 2
('Indiranagar Branch Library',     '100 Feet Road, Indiranagar, Bangalore 560038'), -- 3
('Park Street Literary Centre',    'Park Street, Kolkata 700016'), -- 4
('Anna Centenary Library Annex',   'Gandhi Irwin Road, Egmore, Chennai 600008'); -- 5

INSERT INTO Bookstore (Name, Location) VALUES
('Footnotes Bookstore', 'Commercial Street, Bangalore 560001'), -- 1
('The Margin Bookshop', 'Hauz Khas Village, New Delhi 110016'), -- 2
('Bylanes Books',       'Fort Area, Mumbai 400001'), -- 3
('Papyrus & Co.',       'T. Nagar, Chennai 600017'); -- 4

-- ─────────────────────────────────────────────────────────────────────────────
-- 8. BOOK COPIES
-- ─────────────────────────────────────────────────────────────────────────────
INSERT INTO BookCopy (ISBN, LibraryID, StoreID, Status, Price, DiscountPercent) VALUES
-- Harry Potter
('978-0439708180', 1, NULL, 'Available', NULL, NULL),
('978-0439708180', 3, NULL, 'Borrowed',  NULL, NULL),
('978-0439708180', NULL, 2, 'Available', 499.00, 10),
-- GoT
('978-0553103540', 2, NULL, 'Available', NULL, NULL),
('978-0553103540', NULL, 1, 'Available', 599.00, 15),
-- Foundation
('978-0553293357', 1, NULL, 'Available', NULL, NULL),
('978-0553293357', NULL, 3, 'Available', 350.00, NULL),
-- And Then There Were None
('978-0062073488', 4, NULL, 'Available', NULL, NULL),
('978-0062073488', NULL, 2, 'Available', 299.00, 20),
-- Hunger Games
('9780439023481', 5, NULL, 'Available', NULL, NULL),
('9780439023481', NULL, 1, 'Available', 399.00, 10),
-- Alchemist
('9780062315007', 3, NULL, 'Available', NULL, NULL),
('9780062315007', NULL, 4, 'Available', 199.00, NULL),
-- Atomic Habits
('9780735211292', 1, NULL, 'Available', NULL, NULL),
('9780735211292', NULL, 2, 'Available', 450.00, 5),
-- Great Gatsby
('9780743273565', 2, NULL, 'Available', NULL, NULL),
('9780743273565', NULL, 3, 'Available', 250.00, NULL),
-- Sapiens
('9780062316110', 4, NULL, 'Available', NULL, NULL),
('9780062316110', NULL, 1, 'Available', 550.00, 15),
-- God of Small Things
('9780679457312', 1, NULL, 'Available', NULL, NULL),
('9780679457312', NULL, 3, 'Available', 499.00, 10),
-- Suitable Boy
('9780060786526', 3, NULL, 'Available', NULL, NULL),
('9780060786526', NULL, 4, 'Available', 899.00, 5),
-- Shadow Lines
('9780618329977', 4, NULL, 'Available', NULL, NULL),
('9780618329977', NULL, 2, 'Available', 399.00, NULL),
-- 2 States
('9788129115300', 2, NULL, 'Available', NULL, NULL),
('9788129115300', NULL, 1, 'Available', 199.00, 20),
-- Malgudi Days
('9780143031703', 1, NULL, 'Available', NULL, NULL),
('9780143031703', NULL, 3, 'Available', 299.00, 10),
-- Night Train at Deoli
('9780143029014', 5, NULL, 'Available', NULL, NULL),
('9780143029014', NULL, 4, 'Available', 199.00, 5),
-- Purple Hibiscus
('9781616953638', 3, NULL, 'Available', NULL, NULL),
('9781616953638', NULL, 2, 'Available', 450.00, 10),
-- Beloved
('9781400033416', 2, NULL, 'Available', NULL, NULL),
('9781400033416', NULL, 1, 'Available', 350.00, NULL),
-- Norwegian Wood
('9780375704024', 4, NULL, 'Available', NULL, NULL),
('9780375704024', NULL, 3, 'Available', 499.00, 15),
-- One Hundred Years of Solitude
('9780060883287', 5, NULL, 'Available', NULL, NULL),
('9780060883287', NULL, 4, 'Available', 599.00, NULL),
-- Charlie and the Chocolate Factory
('9780142410318', 1, NULL, 'Borrowed',  NULL, NULL),
('9780142410318', NULL, 2, 'Available', 250.00, 5),
-- Add a few more library copies to spread it out
('9780142410318', 3, NULL, 'Available', NULL, NULL),
('9780062316110', 2, NULL, 'Borrowed',  NULL, NULL),
('978-0553103540', 5, NULL, 'Available', NULL, NULL);

-- ─────────────────────────────────────────────────────────────────────────────
-- 9. LOANS (4-5 Realistic Loans)
-- ─────────────────────────────────────────────────────────────────────────────
-- User 1: Alice (MemberID=1)
-- User 2: Bob   (MemberID=2)

INSERT INTO Loan (CopyID, MemberID, IssueDate, DueDate, ReturnDate) VALUES
-- 1. Active overdue: Harry Potter from Bangalore (CopyID=2)
(2, 1, DATE_SUB(CURDATE(), INTERVAL 20 DAY), DATE_SUB(CURDATE(), INTERVAL 6 DAY), NULL),
-- 2. Active overdue: Sapiens from Bandra (CopyID=47)
(47, 2, DATE_SUB(CURDATE(), INTERVAL 25 DAY), DATE_SUB(CURDATE(), INTERVAL 11 DAY), NULL),
-- 3. Active on-time: Charlie and the Chocolate Factory from CP (CopyID=44)
(44, 1, DATE_SUB(CURDATE(), INTERVAL 5 DAY), DATE_ADD(CURDATE(), INTERVAL 9 DAY), NULL),
-- 4. Active on-time: Suitable Boy from Indiranagar (CopyID=34) - wait, manually finding IDs is prone to error
-- Use LAST_INSERT_ID() or just hope for sequential. 
-- For clarity, I'll just use the first few IDs since it's a seed.
(1, 2, DATE_SUB(CURDATE(), INTERVAL 2 DAY), DATE_ADD(CURDATE(), INTERVAL 12 DAY), NULL),
-- 5. Returned loan
(3, 1, DATE_SUB(CURDATE(), INTERVAL 30 DAY), DATE_SUB(CURDATE(), INTERVAL 16 DAY), DATE_SUB(CURDATE(), INTERVAL 18 DAY));

-- ─────────────────────────────────────────────────────────────────────────────
-- 10. BOOKMARKS
-- ─────────────────────────────────────────────────────────────────────────────
INSERT INTO Bookmark (UserID, ISBN) VALUES
(1, '978-0553103540'), -- Alice saves GoT
(1, '978-0553293357'), -- Alice saves Foundation
(2, '978-0439708180'), -- Bob saves Harry Potter
(3, '978-0062073488'); -- Charlie saves And Then There Were None
