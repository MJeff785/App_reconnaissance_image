import mysql.connector
from mysql.connector import Error
from tkinter import messagebox

class DatabaseConnection:
    def __init__(self):
        self.config = {
            'host': 'localhost',
            'user': 'root',
            'password': '',
            'database': 'lycee_melkior'
        }

    def connect(self):
        try:
            connection = mysql.connector.connect(**self.config)
            if connection.is_connected():
                return connection
        except Error as e:
            messagebox.showerror("Connection Error", f"Error: {e}")
            return None

    def execute_query(self, query, params=None):
        connection = self.connect()
        cursor = None
        if connection:
            try:
                cursor = connection.cursor()
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                
                result = cursor.fetchall() if cursor.description else None
                connection.commit()
                return result
            except Error as e:
                messagebox.showerror("Query Error", f"Error: {e}")
                return None
            finally:
                if cursor:
                    cursor.close()
                connection.close()
        return None

    def test_connection(self):
        connection = self.connect()
        if connection:
            messagebox.showinfo("Success", "Connected to database successfully!")
            connection.close()