-- ArdenLeaf Database Schema

CREATE DATABASE IF NOT EXISTS ardenleaf;
USE ardenleaf;

-- 1. Base User Table
CREATE TABLE IF NOT EXISTS User (
    UserID INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(100) NOT NULL,
    Email VARCHAR(100) UNIQUE NOT NULL,
    PasswordHash VARCHAR(255) NOT NULL,
    UserType ENUM('Member', 'Customer', 'Admin', 'LibraryAdmin', 'StoreAdmin') NOT NULL,
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Multivalued Attribute: User Phone
CREATE TABLE IF NOT EXISTS User_Phone (
    Phone VARCHAR(20) NOT NULL,
    UserID INT NOT NULL,
    PRIMARY KEY (Phone, UserID),
    FOREIGN KEY (UserID) REFERENCES User(UserID) ON DELETE CASCADE
);

-- 3. Specialization: Member
CREATE TABLE IF NOT EXISTS Member (
    UserID INT PRIMARY KEY,
    MembershipDate DATE NOT NULL,
    MaxBooks INT DEFAULT 5,
    FOREIGN KEY (UserID) REFERENCES User(UserID) ON DELETE CASCADE
);

-- 4. Specialization: Customer
CREATE TABLE IF NOT EXISTS Customer (
    UserID INT PRIMARY KEY,
    LoyaltyPoints INT DEFAULT 0,
    FOREIGN KEY (UserID) REFERENCES User(UserID) ON DELETE CASCADE
);

-- 5. Publisher
CREATE TABLE IF NOT EXISTS Publisher (
    PublisherID INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(150) NOT NULL,
    Address TEXT
);

-- 6. Author
CREATE TABLE IF NOT EXISTS Author (
    AuthorID INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(150) NOT NULL
);

-- 7. Book
CREATE TABLE IF NOT EXISTS Book (
    ISBN VARCHAR(20) PRIMARY KEY,
    Title VARCHAR(255) NOT NULL,
    PublisherID INT,
    PublicationYear INT,
    FOREIGN KEY (PublisherID) REFERENCES Publisher(PublisherID) ON DELETE SET NULL
);

-- 8. Many-to-Many: Book - Author
CREATE TABLE IF NOT EXISTS Book_Author (
    ISBN VARCHAR(20),
    AuthorID INT,
    PRIMARY KEY (ISBN, AuthorID),
    FOREIGN KEY (ISBN) REFERENCES Book(ISBN) ON DELETE CASCADE,
    FOREIGN KEY (AuthorID) REFERENCES Author(AuthorID) ON DELETE CASCADE
);

-- 9. Multivalued Attribute: Book Genre
CREATE TABLE IF NOT EXISTS Book_Genre (
    ISBN VARCHAR(20),
    Genre VARCHAR(50),
    PRIMARY KEY (ISBN, Genre),
    FOREIGN KEY (ISBN) REFERENCES Book(ISBN) ON DELETE CASCADE
);

-- 10. Library
CREATE TABLE IF NOT EXISTS Library (
    LibraryID INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(150) NOT NULL,
    Location TEXT NOT NULL
);

-- 11. Bookstore
CREATE TABLE IF NOT EXISTS Bookstore (
    StoreID INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(150) NOT NULL,
    Location TEXT NOT NULL
);

-- 12. Weak Entity/Dependent Table: BookCopy
CREATE TABLE IF NOT EXISTS BookCopy (
    CopyID INT AUTO_INCREMENT PRIMARY KEY,
    ISBN VARCHAR(20) NOT NULL,
    LibraryID INT NULL,          -- NULL if it belongs to a bookstore
    StoreID INT NULL,            -- NULL if it belongs to a library
    Status ENUM('Available', 'Borrowed', 'Sold') DEFAULT 'Available',
    Price DECIMAL(10,2) NULL,    -- Only set for bookstore copies; NULL for library copies
    DiscountPercent INT NULL,    -- Optional discount %; NULL if no discount or library copy
    FOREIGN KEY (ISBN) REFERENCES Book(ISBN) ON DELETE CASCADE,
    FOREIGN KEY (LibraryID) REFERENCES Library(LibraryID) ON DELETE SET NULL,
    FOREIGN KEY (StoreID) REFERENCES Bookstore(StoreID) ON DELETE SET NULL
    -- Note: Library-or-Bookstore constraint enforced at application level
);

-- 13. Loan (Only Members borrow from Libraries)
CREATE TABLE IF NOT EXISTS Loan (
    LoanID INT AUTO_INCREMENT PRIMARY KEY,
    CopyID INT NOT NULL,
    MemberID INT NOT NULL,
    IssueDate DATE NOT NULL,
    DueDate DATE NOT NULL,
    ReturnDate DATE NULL,
    FOREIGN KEY (CopyID) REFERENCES BookCopy(CopyID) ON DELETE CASCADE,
    FOREIGN KEY (MemberID) REFERENCES Member(UserID) ON DELETE CASCADE
);

-- Derived Attribute Example: Fine Calculation View
-- Calculates fine assuming $2 per day late. Fine stops accumulating if returned (or continues if NULL to current date)
CREATE OR REPLACE VIEW LoanFines AS
SELECT 
    l.LoanID,
    l.MemberID,
    l.CopyID,
    l.DueDate,
    l.ReturnDate,
    CASE 
        WHEN l.ReturnDate IS NOT NULL AND l.ReturnDate > l.DueDate THEN DATEDIFF(l.ReturnDate, l.DueDate) * 2.00
        WHEN l.ReturnDate IS NULL AND CURDATE() > l.DueDate THEN DATEDIFF(CURDATE(), l.DueDate) * 2.00
        ELSE 0.00
    END AS FineAmount
FROM Loan l;

-- 14. Bookmark (Users can save books for later)
CREATE TABLE IF NOT EXISTS Bookmark (
    BookmarkID INT AUTO_INCREMENT PRIMARY KEY,
    UserID INT NOT NULL,
    ISBN VARCHAR(20) NOT NULL,
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (UserID) REFERENCES User(UserID) ON DELETE CASCADE,
    FOREIGN KEY (ISBN) REFERENCES Book(ISBN) ON DELETE CASCADE,
    UNIQUE KEY uq_user_isbn (UserID, ISBN)  -- A user cannot bookmark the same book twice
);

-- 15. LocationAdmin (LibraryAdmin or StoreAdmin mapped to exactly one location)
-- Note: MySQL 8.0 forbids CHECK constraints on columns used in ON DELETE SET NULL FK actions.
--       The XOR rule (LibraryID XOR StoreID must be set) is enforced at the application level.
CREATE TABLE IF NOT EXISTS LocationAdmin (
    UserID INT PRIMARY KEY,
    LibraryID INT DEFAULT NULL,
    StoreID INT DEFAULT NULL,
    FOREIGN KEY (UserID) REFERENCES User(UserID) ON DELETE CASCADE,
    FOREIGN KEY (LibraryID) REFERENCES Library(LibraryID) ON DELETE SET NULL,
    FOREIGN KEY (StoreID) REFERENCES Bookstore(StoreID) ON DELETE SET NULL
);
