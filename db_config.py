import mysql.connector


db = mysql.connector.connect(
    host="telesupport-db.cjog40uyo8xw.ap-south-1.rds.amazonaws.com",
    user="admin",
    password="India11tejas",
    database="telesupport",
)

print("Database Connected Successfully")
