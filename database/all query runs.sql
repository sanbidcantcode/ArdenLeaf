UPDATE User SET PasswordHash = 'scrypt:32768:8:1$GrMmi2nFN98Y0rk8$6100c8d263345812a9ca306557ba557d59848a77a8b1d394f489a37a5a65363ff32fde3d5278c6ff9b0dec819d103310e3f8311247b33c91f2141a0186fdc0c7', UserType = 'Admin' WHERE Email = 'admin@ardenleaf.com';
-- 1. Ensure Admin type is allowed
ALTER TABLE User MODIFY UserType ENUM('Member', 'Customer', 'Admin') NOT NULL;

-- 2. Insert the Admin user with the correct hashed password 
-- (I've pre-generated the hash for 'admin123' for you below)
INSERT INTO User (Name, Email, PasswordHash, UserType) 
VALUES ('System Admin', 'admin@ardenleaf.com', 'scrypt:32768:8:1$GrMmi2nFN98Y0rk8$6100c8d263345812a9ca306557ba557d59848a77a8b1d394f489a37a5a65363ff32fde3d5278c66ff9b0dec819d103310e3f8311247b33c91f2141a0186fdc0c7', 'Admin')
ON DUPLICATE KEY UPDATE UserType = 'Admin';
-- Set the password to plain text 'admin123' to match your current code logic
UPDATE User 
SET PasswordHash = 'admin123' 
WHERE Email = 'admin@ardenleaf.com';
