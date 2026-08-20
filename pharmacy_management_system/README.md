# PharmaCare — Pharmacy Management System

This version uses **MySQL instead of MongoDB**. The project covers the uploaded specification's medicine inventory, supplier/customer records, stock monitoring and the frontend module structure. fileciteturn0file0L3-L17

## Stack
- Frontend: HTML, CSS, JavaScript
- Backend: Python, Flask
- Database: MySQL

## Setup

### 1. Create database/tables
Open MySQL Workbench or MySQL command line and run:

```sql
SOURCE backend/schema.sql;
```

### 2. Configure MySQL
Default settings:
- Host: localhost
- User: root
- Password: empty
- Database: pharmacy_management

Or set:
`MYSQL_HOST`, `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_DATABASE`.

### 3. Install packages

```bash
pip install -r requirements.txt
```

### 4. Start Flask

```bash
python backend/app.py
```

Open:

`http://localhost:5000`

## CRUD APIs

Medicines:
- GET `/api/medicines`
- POST `/api/medicines`
- PUT `/api/medicines/<id>`
- DELETE `/api/medicines/<id>`

Suppliers and Customers have the same CRUD pattern.

The original project specification lists MySQL as an allowed database option alongside MongoDB; this version selects MySQL. fileciteturn0file0L72-L81
