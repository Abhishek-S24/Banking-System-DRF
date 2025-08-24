# Banking System with REST API

## Project Overview
**Banking System with REST API** is a comprehensive banking application built using Django and Django REST Framework. This project enables users to manage bank accounts, perform transactions, and ensures security and performance optimization.  

This project was developed as part of an assignment aimed at building a feature-rich banking platform with dynamic roles, external fund transfers, multi-currency support, and performance-focused architecture.

---

## Objective
- Implement a fully functional banking system with a RESTful API interface.
- Support secure user authentication and authorization.
- Enable multi-account management and external fund transfers.
- Optimize for performance, scalability, and multi-tenancy.

---

## Features

### 1. User Registration and Login
- User registration and authentication via Django's built-in system.
- Two-Factor Authentication (2FA) using OTP via email/mobile.

### 2. Account Management
- Create and manage multiple bank accounts per user.
- Unique account numbers are auto-generated.
- Admins can perform batch account creation and update operations.

### 3. Transactions
- Deposit, withdraw, and transfer money between accounts.
- Transaction amounts are validated.
- Detailed transaction history with filters by date and transaction type.

### 4. External Fund Transfer
- Secure fund transfer to other users within the system.
- Multi-currency support (USD, GBP, EUR) with real-time conversion using ExchangeRatesAPI and a 0.01% spread.

### 5. User Roles and Permissions
- Dynamic user roles with customizable permissions.
- Admins can assign/remove roles and permissions for users and groups.

### 6. Security Measures
- Two-factor authentication and secure password storage.
- Protection against common vulnerabilities (SQL injection, CSRF, etc.).

### 7. Performance Optimization
- Efficient handling of large tables with 100+ columns for analytical purposes.
- Caching strategies implemented to improve API response times.
- Support for multiple time zones and multi-tenancy.

### 8. Testing
- Comprehensive unit and integration tests covering all major features.
- Transactions and role management fully tested.

### 9. Documentation
- API documented using **drf-yasg** (Swagger/OpenAPI).
- Postman collection included for testing all endpoints.

---

## Project Architecture Diagram

```plaintext
+---------------------+       +---------------------+       +----------------------+
|      Frontend       | <---> |       API Layer     | <---> |    Django Backend    |
| (Postman / Swagger) |       | Django REST Framework|      |  Models, Serializers |
+---------------------+       +---------------------+       +----------------------+
                                       |
                                       v
                                +--------------------+
                                | Database (SQLite / |
                                | PostgreSQL / MySQL)|
                                +--------------------+
                                        |
                                        v
                                +--------------------+
                                | External Services  |
                                |                    |
                                |  ExchangeRatesAPI  |
                                +--------------------+
```
- Frontend / API Testing: Postman collection or Swagger UI.

- API Layer: Handles HTTP requests, authentication, permissions, and validation.

- Django Backend: Business logic, account management, transactions, roles, and permissions.

- Database: Stores user data, account information, transactions, roles, and permissions.

- External Services: Currency exchange API for multi-currency transfers.

## Installation
Using Docker (Recommended)

### Step 1: Build and run containers

docker-compose up --build


### Step 2: Apply migrations

docker-compose exec web python manage.py migrate


### Step 3: Create superuser

docker-compose exec web python manage.py createsuperuser


### Step 4: Access the application

API: http://localhost:8000/

Swagger docs: http://localhost:8000/swagger/

Postman Link : https://documenter.getpostman.com/view/47793871/2sB3BLjTY6

## Without Docker

### Clone the repository:

git clone <repo-url>
cd Banking-System-DRF


### Create a virtual environment and install dependencies:

python -m venv env
source env/bin/activate  # Linux/Mac
env\Scripts\activate     # Windows
pip install -r requirements.txt


### Apply migrations and create superuser:

python manage.py migrate
python manage.py createsuperuser


### Run the server:

python manage.py runserver


## API Documentation

- All APIs are documented using Swagger.

- Postman collection is included in the repository for quick testing.

- Supports operations for users, accounts, transactions, roles, and permissions.

## Running Test Cases
### Using Docker

Run all tests:

docker-compose exec web python manage.py test

### Without Docker

Ensure your virtual environment is activated, then run:

python manage.py test


To test specific apps:

python manage.py test Transactions
python manage.py test Roles


#### Notes:

- Tests cover user registration, login, account management, deposits, withdrawals, transfers, transaction history, and role/permission management.

## Achievements / Assignment Highlights

- **Complete Banking System** – End-to-end REST API implementation for core banking operations.  
- **Role-Based Access Control** – Dynamic user roles and permissions management.  
- **Multi-Currency Transactions** – Support for external and inter-account transfers with real-time currency conversion.  
- **Enhanced Security** – OTP-based two-factor authentication (2FA) for sensitive operations.  
- **High Performance** – Pagination implemented for data-heavy transaction and analytics tables.  
- **Comprehensive Logging** – Middleware-based activity logging per action type, including user login and transaction activities.  
- **Excel Export** – Transaction history can be exported directly as Excel files for reporting and analysis.  
- **Containerized Deployment** – Dockerized setup for seamless installation and deployment.  
- **Reliable Testing** – Full coverage with unit and integration tests.  
- **API Documentation** – Available via Swagger UI and Postman collection for easy exploration.  