#!/usr/bin/env python3
"""
Script to create user_login_sessions table.
Uses credentials from .env file.
"""
import os
import sys
from pathlib import Path

# Load .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("Warning: python-dotenv not installed. Using environment variables directly.")

# Get database credentials from .env
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_NAME = os.getenv("DB_NAME", "secfiling")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

# SQL to create table
CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS `user_login_sessions` (
  `session_id` INT NOT NULL AUTO_INCREMENT,
  `user_email` VARCHAR(255) DEFAULT NULL,
  `user_nicename` VARCHAR(255) DEFAULT NULL,
  `user_display_name` VARCHAR(255) DEFAULT NULL,
  `token` TEXT,
  `login_at` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
  `last_activity` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `membership_id` VARCHAR(32) DEFAULT NULL,
  `membership_type` VARCHAR(255) DEFAULT NULL,
  PRIMARY KEY (`session_id`),
  KEY `idx_user_email` (`user_email`),
  KEY `idx_login_at` (`login_at`)
) ENGINE=InnoDB 
DEFAULT CHARSET=utf8mb4 
COLLATE=utf8mb4_0900_ai_ci;
"""

def create_table():
    """Create the user_login_sessions table using PyMySQL."""
    try:
        import pymysql
    except ImportError:
        print("Error: PyMySQL not installed.")
        print("Install with: pip install pymysql")
        sys.exit(1)
    
    print(f"Connecting to database: {DB_NAME} on {DB_HOST}:{DB_PORT}")
    print(f"User: {DB_USER}")
    
    try:
        # Connect to database
        connection = pymysql.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            charset='utf8mb4'
        )
        
        with connection.cursor() as cursor:
            print("Creating user_login_sessions table...")
            cursor.execute(CREATE_TABLE_SQL)
            connection.commit()
            
            # Verify table was created
            cursor.execute("SHOW TABLES LIKE 'user_login_sessions'")
            result = cursor.fetchone()
            
            if result:
                print("✅ Table 'user_login_sessions' created successfully!")
                
                # Show table structure
                cursor.execute("DESCRIBE user_login_sessions")
                columns = cursor.fetchall()
                print("\nTable structure:")
                print(f"{'Field':<20} {'Type':<30} {'Null':<10} {'Key':<10}")
                print("-" * 70)
                for col in columns:
                    print(f"{col[0]:<20} {str(col[1]):<30} {col[2]:<10} {col[3]:<10}")
            else:
                print("❌ Failed to create table.")
                
    except pymysql.Error as e:
        print(f"❌ Database error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)
    finally:
        if 'connection' in locals():
            connection.close()
            print("\nDatabase connection closed.")

def main():
    """Main entry point."""
    print("=" * 60)
    print("User Login Sessions Table Creation Script")
    print("=" * 60)
    print()
    
    # Check if running from correct directory
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    # Try to load .env from project root
    env_file = project_root / ".env"
    if env_file.exists():
        print(f"Loading .env from: {env_file}")
        load_dotenv(env_file)
    
    # Re-read credentials after loading .env
    global DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = int(os.getenv("DB_PORT", "3306"))
    DB_NAME = os.getenv("DB_NAME", "secfiling")
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    
    print()
    create_table()

if __name__ == "__main__":
    main()
