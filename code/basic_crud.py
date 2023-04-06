import mysql.connector
from mysql.connector import Error

# connect to MySql Database
def connect():
    try:
        connection = mysql.connector.connect(
            host='35.193.136.209',
            database='YoutubeTrending',
            user='root',
            password='test1234')
        if connection.is_connected():
            print('Connected to MySQL database')
            return connection
    except Error as e:
        print(f'Error connecting to MySQL database: {e}')

# Closes the connection to the MySQL database
def close_connection(connection):
    if connection.is_connected():
        connection.close()
        print('Connection to MySQL database closed')

# VERY BASIC insert operation
def create_record(connection, table_name, record_values):
    cursor = connection.cursor()
    sql = f"INSERT INTO {table_name} VALUES {record_values}"
    cursor.execute(sql)
    connection.commit()
    print(f'{cursor.rowcount} record inserted into {table_name} table')

def read_records(connection, table_name):
    cursor = connection.cursor()
    sql = f"SELECT * FROM {table_name}"
    cursor.execute(sql)
    records = cursor.fetchall()
    for record in records:
        print(record)


def update_record(connection, table_name, update_values, search_condition):
    cursor = connection.cursor()
    sql = f"UPDATE {table_name} SET {update_values} WHERE {search_condition}"
    cursor.execute(sql)
    connection.commit()
    print(f'{cursor.rowcount} record(s) updated in {table_name} table')

def delete_record(connection, table_name, search_condition):
    cursor = connection.cursor()
    sql = f"DELETE FROM {table_name} WHERE {search_condition}"
    cursor.execute(sql)
    connection.commit()
    print(f'{cursor.rowcount} record(s) deleted from {table_name} table')

def search_records(connection, table_name, search_condition):
    cursor = connection.cursor()
    sql = f"SELECT * FROM {table_name} WHERE {search_condition}"
    cursor.execute(sql)
    results = cursor.fetchall()
    print(f'{cursor.rowcount} record(s) found in {table_name} table')
    for row in results:
        print(row)

# insert new user: TO DO
'''
ask for a video
check if video exists in VideoInfo Table
add it if it doesnt
add person to creators
add person to website users
'''

def display_menu():
    """Displays the main menu"""
    print('\n=== Main Menu ===')
    print('1. Insert new record')
    print('2. Read all records')
    print('3. Update existing record')
    print('4. Delete existing record')
    print('5. Search for records')
    print('0. Exit')

def main():
    """Main program logic"""
    connection = connect()
    while True:
        display_menu()
        choice = input('Enter your choice: ')
        if choice == '1':
            table_name = input('Enter table name: ')
            record_values = input('Enter record values in the form (value1, value2, value3, ...): ')
            create_record(connection, table_name, record_values)
        elif choice == '2':
            table_name = input('Enter table name: ')
            read_records(connection, table_name)
        elif choice == '3':
            table_name = input('Enter table name: ')
            update_values = input('Enter the updated values as a SET clause: ')
            search_condition = input('Enter the search condition as a WHERE clause: ')
            update_record(connection, table_name, update_values, search_condition)
        elif choice == '4':
            table_name = input('Enter table name: ')
            search_condition = input('Enter the search condition as a WHERE clause: ')
            delete_record(connection, table_name, search_condition)
        elif choice == '5':
            table_name = input('Enter table name: ')
            search_condition = input('Enter the search condition as a WHERE clause: ')
            search_records(connection, table_name, search_condition)
        elif choice == '0':
            connection.close()
            print('Goodbye!')
            break
        else:
            print('Invalid choice. Please try again.')

main()

