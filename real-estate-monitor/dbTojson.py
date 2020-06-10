import MySQLdb
import json
import sys

tn = sys.argv[1]

db = MySQLdb.Connect(
    host = 'localhost',
    user= 'kevin',
    password = 'Montera93',
    database = 'apartment_monitoring'
)

cursor = db.cursor()

query = "SELECT * FROM apartments_{}".format(tn)

with open('{}.json'.format(tn), 'a+') as file:

    with db.cursor(MySQLdb.cursors.DictCursor) as cursor:
        cursor.execute(query)
        data = cursor.fetchall()
        file.write(json.dumps(data,indent=4))