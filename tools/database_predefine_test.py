import sqlite3

# Connect to the database
db_path = '/workspaces/Project_APS/parking_lot_webapp/instance/db.sqlite'
connection = sqlite3.connect(db_path)
cursor = connection.cursor()

# Insert data into the table
insert_data_parkingslot_query = '''
INSERT INTO parking_slot (slot_number, status)
VALUES (?, ?)
'''

insert_data_vehicle_query = '''
INSERT INTO vehicle (license_plate, status, owner_id)
VALUES (?, ?, ?)
'''

# Sample data to insert
parkingslot_data = [
    ('A1', 'free'),
    ('A2', 'free'),
    ('A3', 'free'),
    ('A4', 'free'),
    ('A5', 'free'),
]

# Sample data to insert
vehicle_data = [
    ('AB123', 'not-parked', 1),
    ('CD456', 'not-parked', 1),

]

# Delete all data from the table
delete_parking_slot_query = f'DELETE FROM parking_slot'
delete_vehicle_query = f'DELETE FROM vehicle'
cursor.execute(delete_parking_slot_query)
cursor.execute(delete_vehicle_query)
connection.commit()

# Execute the INSERT query for all data at once 
cursor.executemany(insert_data_parkingslot_query, parkingslot_data)
cursor.executemany(insert_data_vehicle_query, vehicle_data)

# Commit the changes and close the connection
connection.commit()
connection.close()

print("Data inserted successfully.")
