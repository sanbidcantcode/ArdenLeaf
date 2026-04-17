import mysql.connector

try:
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='Baban_069',
        database='ardenleaf',
        port=3306
    )
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT Name, Email, Password, UserType FROM User')
    users = cursor.fetchall()
    for u in users:
        print(f"Name: {u['Name']}, Email: {u['Email']}, Password: {u['Password']}, Type: {u['UserType']}")
    cursor.close()
    conn.close()
except Exception as e:
    print(f"Error: {e}")
