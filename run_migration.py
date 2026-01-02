"""
Migration script to add is_read column to messages table
Run this script to update your existing database
"""
import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

def run_migration():
    try:
        conn = pymysql.connect(
            host=os.getenv("MYSQL_HOST", "localhost"),
            user=os.getenv("MYSQL_USER", "root"),
            password=os.getenv("MYSQL_PASSWORD", ""),
            database=os.getenv("MYSQL_DB", "CipherCoreDB"),
            cursorclass=pymysql.cursors.DictCursor
        )
        
        with conn.cursor() as cursor:
            # Check if column already exists
            cursor.execute("""
                SELECT COUNT(*) as count
                FROM information_schema.COLUMNS
                WHERE TABLE_SCHEMA = %s
                AND TABLE_NAME = 'messages'
                AND COLUMN_NAME = 'is_read'
            """, (os.getenv("MYSQL_DB", "CipherCoreDB"),))
            
            result = cursor.fetchone()
            
            if result['count'] > 0:
                print("[OK] Column 'is_read' already exists. No migration needed.")
            else:
                print("Adding 'is_read' column to messages table...")
                cursor.execute("""
                    ALTER TABLE messages 
                    ADD COLUMN is_read TINYINT(1) DEFAULT 0 AFTER signature
                """)
                conn.commit()
                print("[OK] Migration completed successfully!")
        
        conn.close()
        
    except Exception as e:
        print(f"[ERROR] Migration failed: {str(e)}")
        print("\nYou can also run the SQL manually:")
        print("mysql -u root -p CipherCoreDB < migration_add_is_read.sql")

if __name__ == "__main__":
    print("CipherCore Database Migration")
    print("=" * 40)
    run_migration()

