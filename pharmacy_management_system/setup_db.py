import mysql.connector
from mysql.connector import Error
import os

DB_CONFIG = {
    "host": os.getenv("MYSQL_HOST", "localhost"),
    "user": os.getenv("MYSQL_USER", "root"),
    "password": os.getenv("MYSQL_PASSWORD", "Dhina@2706"),
}

def setup_database():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Drop existing database if it exists
        cursor.execute("DROP DATABASE IF EXISTS pharmacy_management")
        conn.commit()
        
        # Create database
        cursor.execute("CREATE DATABASE IF NOT EXISTS pharmacy_management")
        cursor.execute("USE pharmacy_management")
        
        # Create medicines table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS medicines (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(150) NOT NULL,
                category VARCHAR(50) NOT NULL,
                batch VARCHAR(80) NOT NULL,
                price DECIMAL(10,2) NOT NULL,
                stock INT NOT NULL DEFAULT 0,
                expiry DATE NOT NULL,
                supplier VARCHAR(150) DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create suppliers table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS suppliers (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(150) NOT NULL,
                phone VARCHAR(30) DEFAULT '',
                email VARCHAR(150) DEFAULT '',
                extra VARCHAR(200) DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create customers table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(150) NOT NULL,
                phone VARCHAR(30) DEFAULT '',
                email VARCHAR(150) DEFAULT '',
                extra VARCHAR(250) DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Insert sample medicines
        cursor.execute("""
            INSERT INTO medicines (name, category, batch, price, stock, expiry, supplier)
            SELECT 'Paracetamol 500mg', 'Tablet', 'PCM-2601', 25.00, 120, '2027-05-30', 'MediSupply'
            WHERE NOT EXISTS (SELECT 1 FROM medicines)
        """)
        
        cursor.execute("""
            INSERT INTO medicines (name, category, batch, price, stock, expiry, supplier)
            SELECT 'Amoxicillin 500mg', 'Capsule', 'AMX-2602', 85.00, 8, '2027-02-15', 'HealthCare Distributors'
            WHERE (SELECT COUNT(*) FROM medicines) = 1
        """)
        
        cursor.execute("""
            INSERT INTO medicines (name, category, batch, price, stock, expiry, supplier)
            SELECT 'Cough Syrup', 'Syrup', 'CS-2603', 110.00, 32, '2026-10-20', 'Wellness Pharma'
            WHERE (SELECT COUNT(*) FROM medicines) = 2
        """)
        
        conn.commit()
        print("✓ Database setup completed successfully!")
        print("✓ Database 'pharmacy_management' created")
        print("✓ Tables created: medicines, suppliers, customers")
        print("✓ Sample data inserted")
        
        cursor.close()
        conn.close()
        
    except Error as e:
        print(f"✗ Error setting up database: {e}")
        return False
    
    return True

if __name__ == "__main__":
    setup_database()
