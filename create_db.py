import sqlite3

DB_PATH = 'user_data.db'  # Относительный путь

def create_database():
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    name TEXT,
                    city TEXT
                )
            ''')
            conn.commit()
            print(f"Таблица 'users' создана в базе {DB_PATH}!")
    except sqlite3.Error as e:
        print(f"Ошибка при создании таблицы: {e}")
    except Exception as e:
        print(f"Неожиданная ошибка: {e}")

if __name__ == "__main__":
    create_database()