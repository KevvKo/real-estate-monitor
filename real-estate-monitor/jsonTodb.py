import json
import MySQLdb
import sys

town = sys.argv[1]

with open ("./{}.json".format(town)) as file:
    data = file.read()
    json = json.loads(data)

#handling the database
db = MySQLdb.Connect(
    host = 'localhost',
    user= 'kevin',
    password = 'Montera93',
    database = 'apartment_monitoring'
)

cursor = db.cursor()

#loops through every jsonline, creating a hash and check, if the current hash already exist

for entry in json:
     
    #creating the query and insert the data to the databasw
    order = 'INSERT INTO apartments_{} (domain, expose, date, coldrent, roomnumber, surface, sidecosts, street, postcode, town, latitude, longitude, hash) VALUES (%s, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'.format(town.lower())
    values = (entry['domain'], int(entry['expose']), entry['date'],entry['coldrent'], entry['roomnumber'], entry['surface'], entry['sidecosts'], entry['street'], entry['postcode'], entry['town'], entry['latitude'], entry['longitude'], entry['hash']) 
    
    #chekcs, if the current query is already in the db
    sql = 'SELECT * FROM apartments_{} WHERE expose={} AND domain="{}"'.format(town.lower(), entry['expose'] , entry['domain'])

    cursor.execute(sql)

    if(cursor.rowcount == 0):

        cursor.execute(order, values)
        db.commit()
    else: continue