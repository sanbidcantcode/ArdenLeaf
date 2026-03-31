# SPEC: ArdenLeaf — Centralized Book Discovery Platform

## Vision
ArdenLeaf is a centralized platform designed to connect multiple libraries and bookstores, providing a single interface for book discovery, availability checking, and borrowing. It aims to empower book enthusiasts by centralizing the search process and facilitating easy access to literary resources.

## Core Objectives
- **Centralized Search**: Enable users to search for books across various libraries and bookstores simultaneously.
- **Availability Checking**: Provide real-time (or near real-time) availability status for books at different locations.
- **Resource Management**: Facilitate book borrowing from libraries and track user loans and overdue fines.
- **User Engagement**: Offer a user-friendly interface for book discovery and management.

## Key Features
1. **Unified Search Engine**: Search by title, author, ISBN, or genre across all connected sources.
2. **Detailed Resource Views**: View book details, availability at specific libraries/bookstores, and related information.
3. **Borrowing System**: Allow registered users (Members) to borrow books from libraries and track their loan history.
4. **Loan Tracking & Fines**: Display active loans, calculate overdue fines, and manage loan returns.
5. **Location Discovery**: Browse and list available libraries and bookstores in the system.

## Technical Architecture (Initial)
- **Backend**: Python-based Flask application.
- **Database**: MySQL for structured data storage (Users, Books, Libraries, Loans).
- **Frontend**: HTML5, Vanilla CSS, and Jinja templates for dynamic content rendering.
- **Communication**: RESTful-like routes for data interaction.

## Future Plans
- **Real-time Notifications**: Alert users of upcoming loan due dates and new book arrivals.
- **Integration with External APIs**: Expand the discovery scope by integrating with third-party book data providers (e.g., Google Books, OpenLibrary).
- **Enhanced User Profiles**: Add personalized recommendations and book reviews.

## Differentiators
- India-focused platform bridging the gap between large libraries and small independent bookstores
- Unlike WorldCat, designed specifically for the Indian market with support for small bookshops
- Location-based discovery showing nearest available library or bookstore first

## Scope for Current Build
- Admin panel for adding books, managing copies, and onboarding libraries/bookstores
- Mobile responsive frontend
- Deployed live with a public URL