import pyodbc

# Bağlantı dizesini güncelleyin
connection_string = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=81.8.112.74,1433;UID=sql-readonlyuser;PWD=Selim12345;DATABASE=LOGO'

try:
    conn = pyodbc.connect(connection_string)
    print("Bağlantı başarılı!")
    conn.close()
except Exception as e:
    print(f"Bağlantı başarısız: {e}")
