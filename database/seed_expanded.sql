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
('Alice Smith',   'alice@example.com',   'scrypt:32768:8:1$K4GpO1WgtGzyL9Zd$958520cae2825b7a141314e47237e540488fffaed28369e44a8c1ec6eaa710b5d71d8ce91a310224ed3162de5d8482102901f495cb41323df8cde654abf69e65', 'Member'),
('Bob Johnson',   'bob@example.com',     'scrypt:32768:8:1$BSpYehIKl5SIvP4v$90d6454a24d0606ad0cd7648155ca53dfa60b64363613abe19cc38d4c9d86ad63b35801e920fca4cda4e2d7126870b08de7992a0c7d1eb0b5d5e4084e26d2d53', 'Member'),
('Charlie Brown', 'charlie@example.com', 'scrypt:32768:8:1$N01LACki46kFQ4Eh$95bb2d7e3e590cf852438811ee128953b14067d7d8730957a3d554f21f31583b5f2afa12c426b3adf807a312f24930a694a5ddca726da571b3e060a0ddaa7105', 'Customer'),
('Diana Prince', 'diana@example.com',   'scrypt:32768:8:1$LCOIHIJhRmHyY0qv$32c6fb093c8751b1761ffb63b27159124a55ca70a2c068760c1b17c7562e3aea29f82c7eb7dd019338a32f445f47d12f3ad5e896ce59cdbbecbe85113c06cbd9', 'Customer');

-- Staff accounts (Admin, LibraryAdmins, StoreAdmins)
-- Passwords: admin123, libpass1, libpass2, storepass1, storepass2
INSERT INTO User (Name, Email, PasswordHash, UserType) VALUES
('System Admin',     'admin@ardenleaf.com',   'scrypt:32768:8:1$5xclqzYH2CvJiHdj$dc12f5ea77b036c1032503f3025d41cae682dc1ed2acc9f97662cc7c7926e779c840ee07f828b43a9bfdaf011f65bb14d0bde20b44e9aad28ee8d33735e94d99', 'Admin'),
('Priya Sharma',     'lib1@ardenleaf.com',    'scrypt:32768:8:1$VufG7yqJxVTxGV57$0301b772240cb8b413aac5d1777a49809e327273fd40e727a772c444d4be1bd17f0c7ea870f1f89c9a06773aa02a775fb3241e1a393605c52efb89ea9757bae0', 'LibraryAdmin'),
('Rajan Mehta',      'lib2@ardenleaf.com',    'scrypt:32768:8:1$CXf9ScBICCL6aAEy$d06ac9dd381c23a8e0a14dd50cd5c1ef310628439c30e7bd0c7d5f9a4306e2f973d1b087351288bef5473946895fcc9f104745a2c1b7550c6e32005af3a37a63', 'LibraryAdmin'),
('Kavya Nair',       'store1@ardenleaf.com',  'scrypt:32768:8:1$H2Y4IhZFnh727BGK$f3215748d6354291697b39ffd799f38fbeb3fc57181ce0efa2e7fc328aefa1bf0f7723489691dc389cab4b473fda9d95392a7a95ef7fcccf3e3984f4e93d3aaa', 'StoreAdmin'),
('Aman Verma',       'store2@ardenleaf.com',  'scrypt:32768:8:1$Yo3sHpI7sb6ezqNq$2f49c070a057becbf81208fe8ebdab8930ab7538b15f4ebb73d2f18a035a1f7c7bb205955fede097d0ccd147835ec22edbc52581c485654d963a3c887c799c14', 'StoreAdmin');

-- UserIDs after insert: 1=Alice, 2=Bob, 3=Charlie, 4=Diana, 5=Admin, 6=LibAdmin1, 7=LibAdmin2, 8=StoreAdmin1, 9=StoreAdmin2

INSERT INTO Member (UserID, MembershipDate, MaxBooks) VALUES
(1, '2023-01-15', 5),
(2, '2023-06-20', 5);

INSERT INTO Customer (UserID, LoyaltyPoints) VALUES
(3, 120),
(4, 300);

-- LocationAdmin rows are inserted after Libraries and Bookstores below

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

-- Link owners to their locations
-- LibraryIDs: 1=Connaught Place, 2=Bandra | StoreIDs: 1=Footnotes, 2=The Margin
INSERT INTO LocationAdmin (UserID, LibraryID, StoreID) VALUES
(6, 1, NULL),   -- Priya → Connaught Place Public Library
(7, 2, NULL),   -- Rajan → Bandra Reading House
(8, NULL, 1),   -- Kavya → Footnotes Bookstore
(9, NULL, 2);   -- Aman  → The Margin Bookshop

-- ─────────────────────────────────────────────────────────────────────────────
-- 8. BOOK COPIES
-- ─────────────────────────────────────────────────────────────────────────────
INSERT INTO BookCopy (ISBN, LibraryID, StoreID, Status, Price, DiscountPercent) VALUES
-- Harry Potter
('978-0439708180', 1, NULL, 'Borrowed',  NULL, NULL),
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
('9780062316110', 4, NULL, 'Borrowed', NULL, NULL),
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
-- 1. Active overdue: Harry Potter from Bangalore (CopyID=2, Library 3)
(2,  1, DATE_SUB(CURDATE(), INTERVAL 20 DAY), DATE_SUB(CURDATE(), INTERVAL 6 DAY),  NULL),
-- 2. Active overdue: Sapiens from Kolkata (CopyID=18, Library 4)
(18, 2, DATE_SUB(CURDATE(), INTERVAL 25 DAY), DATE_SUB(CURDATE(), INTERVAL 11 DAY), NULL),
-- 3. Active on-time: Charlie and the Chocolate Factory from CP (CopyID=40, Library 1)
(40, 1, DATE_SUB(CURDATE(), INTERVAL 5 DAY),  DATE_ADD(CURDATE(), INTERVAL 9 DAY),  NULL),
-- 4. Active on-time: Harry Potter from CP (CopyID=1, Library 1)
(1,  2, DATE_SUB(CURDATE(), INTERVAL 2 DAY),  DATE_ADD(CURDATE(), INTERVAL 12 DAY), NULL),
-- 5. Returned loan (store copy excluded — only library copies are borrowed)
(4,  1, DATE_SUB(CURDATE(), INTERVAL 30 DAY), DATE_SUB(CURDATE(), INTERVAL 16 DAY), DATE_SUB(CURDATE(), INTERVAL 18 DAY));

-- ─────────────────────────────────────────────────────────────────────────────
-- 10. BOOKMARKS
-- ─────────────────────────────────────────────────────────────────────────────
INSERT INTO Bookmark (UserID, ISBN) VALUES
(1, '978-0553103540'), -- Alice saves GoT
(1, '978-0553293357'), -- Alice saves Foundation
(2, '978-0439708180'), -- Bob saves Harry Potter
(3, '978-0062073488'); -- Charlie saves And Then There Were None
