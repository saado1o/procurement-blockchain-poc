Blockchain Procurement Management System


A secure, role-based procurement application built with Flask, integrating with Ethereum blockchain smart contracts for tender management, bidding, and purchase order approval. The app uses Flask-Login for authentication, Flask-WTF for form handling & CSRF protection, and SQLAlchemy ORM with a MySQL database backend.

Features
User Roles: Admin, Bidder, PPRA Officer (Public Procurement Regulatory Authority)

User Authentication: Secure registration and login with password hashing and CSRF protection.

Tender Management:

Admins can create new tenders with PDF documents and deploy blockchain smart contracts to track tenders.

Tenders have statuses: active, closed, PO awarded.

Bidding System:

Bidders can view active tenders and submit bids with ETH amounts.

Admins approve or reject bids.

Purchase Order Award:

PPRA Officers review approved bids and award purchase orders.

Tender status updates accordingly.

PPRA Queries:

PPRA Officers can send queries about procurement cases to Admins from tender details.

Admins can view and respond to these queries in a dedicated admin interface.

Blockchain Integration:

Tender contracts deployed and tracked on Ethereum (e.g., Ganache local blockchain).

Transaction hashes optionally stored for traceability.

File Uploads:

Tender documents uploaded in PDF format with size limits.

Secure Forms:

All forms include CSRF tokens.

Flask-WTF and Flask-Login ensure session and request security.

Clean UI:

Responsive Bootstrap 5 layout.

Role-aware navigation and views.

System Architecture
Backend: Flask web app with routes for user auth, tender/bid management, and blockchain contract deployment.

Database: MySQL with SQLAlchemy ORM models for Users, Tenders, Bids, and PPRA Queries.

Blockchain: Solidity smart contracts compiled and deployed via Web3.py and py-solc-x libraries to a local Ethereum node (e.g., Ganache).

Templates: Jinja2 HTML templates with Bootstrap styling.

Forms: Flask-WTF forms manage input validation and CSRF tokens.

Installation and Setup
Clone the repository:

bash
git clone https://github.com/yourusername/flask-blockchain-procurement.git
cd flask-blockchain-procurement
Set up a Python virtual environment and install dependencies:

bash
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
Configure the MySQL database:

Create a database named purchase.

Update the connection URI in app.py (app.config['SQLALCHEMY_DATABASE_URI']) with your MySQL credentials.

Install and run a local Ethereum RPC node:

Use Ganache for local blockchain simulation.

Make sure Ganache is running at http://127.0.0.1:7545.

Compile and place Solidity contracts:

Place your Solidity contract (TenderContract.sol) inside the smart_contract/ directory.

The app uses py-solc-x to compile the contract at runtime.

Run database migrations or create tables:

bash
python app.py
The app will create necessary tables on startup.

Run the Flask app:

bash
python app.py
Access the app at: http://127.0.0.1:5000

Usage Workflow
Register users in different roles (Admin, Bidder, PPRA Officer).

Admin:

Log in and create new tenders by uploading tender description and documents.

Deploy blockchain contracts automatically during tender creation.

View bids on tenders and approve or reject each bid.

Bidder:

Log in and browse active tenders.

Submit bids with bid amounts for tenders.

Update bids if needed until approval.

PPRA Officer:

Log in and view tender details.

Submit queries regarding procurement cases to admins.

Approve purchase orders by selecting from approved bids.

Admin:

Review and respond to PPRA queries in their admin interface.

Security Features
Password hashing and verification via Werkzeug.

CSRF protection with Flask-WTF on all forms.

Role-based access control restricting sensitive actions.

Secure file handling with filename sanitation.

Session management with Flask-Login.

Dependencies
Flask

Flask-Login

Flask-WTF

Flask-SQLAlchemy

PyMySQL

Web3.py

py-solc-x

Werkzeug

Bootstrap 5 (via CDN)

Contributing
Contributions and bug reports are welcome. Please open issues or pull requests in the GitHub repository.

License
Specify your project license here (e.g., MIT License).

Contact
For support or questions, contact [your email or GitHub profile].

