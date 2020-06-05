import psycopg2

db_host = "demo-database-1.cvii1d1fvgqo.us-west-1.rds.amazonaws.com"
db_name = "image_gallery"
db_user = "image_gallery"

password_file = "/home/ec2-user/.image_gallery_config"

connection = None

def get_password():
    f = open(password_file, "r")
    result = f.readline()
    f.close()
    return result[:-1]

def connect():
    global connection
    connection = psycopg2.connect(host=db_host, dbname=db_name, user=db_user, password=get_password())

def execute(query,args=None):
    global connection
    cursor = connection.cursor()
    if not args:
        cursor.execute(query)
    else:
        cursor.execute(query, args)    
    return cursor

def list_users():
    print("list_users") 
    row_string = "{user_name:10}\t{password:10}\t{full_name:20}"
    print(row_string.format("username","password","full name"))
    print("---------------------------------------------")
    for row in execute('select * from users'):
        print(row_string.format(row[0],row[1],row[2]))
        
def add_user():
    print("add_user")
    
def edit_user():
    print("edit_user")
    
def delete_user():
    print("delete_user")
    
def quit_menu():
    print("quit_menu")

def main():
    connect()
    
    while True:
        print("1)  List users")
        print("2)  Add users")
        print("3)  Edit user")
        print("4)  Delete user")
        print("5)  Quit")
    
        command = input("Enter command> ")
        if command == "1":
            list_users()
        elif command == "2":
            add_user()
        elif command == "3":
            edit_user()
        elif command == "4":
            delete_user()
        elif command == "5":
            quit_menu()
            break
        else: 
            print("Invalid command entered, try again; if you dare.")

if __name__ == '__main__':
    main()