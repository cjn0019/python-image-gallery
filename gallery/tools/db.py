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
    row_string = "{username:10}\t{password:10}\t{full_name:20}"
    print(row_string.format(username="username",password="password",full_name="full name"))
    print("---------------------------------------------")
    for row in execute('select * from users'):
        print(row_string.format(username=row[0],password=row[1],full_name=row[2]))
    print()
        
def add_user(username,password,full_name):
    if execute("SELECT * FROM users WHERE username=%s;",(username,)).rowcount == 0: 
        execute("INSERT INTO users (username, password, full_name) VALUES (%s,%s,%s);",(username,password,full_name))
    else:
        print("Error:  user already exists.")
    
def edit_user(username,password,full_name):
    if execute("SELECT * FROM users WHERE username=%s;",(username,)).rowcount == 0:
        print("No such user.")
    elif password != "" and full_name != "":
        execute("UPDATE users SET password=%s,full_name=%s WHERE username=%s;",(password,full_name,username))
    elif password != "" and full_name == "":
        execute("UPDATE users SET password=%s WHERE username=%s;",(password,username))
    elif password == "" and full_name != "":
        execute("UPDATE users SET full_name=%s WHERE username=%s;",(full_name,username))
        
def delete_user(username):
    execute("DELETE FROM users WHERE username=%s;",(username,))
    
def quit_menu():
    print("Bye.")
    
def main():
    connect()
    
    while True:
        print("1)  List users")
        print("2)  Add users")
        print("3)  Edit user")
        print("4)  Delete user")
        print("5)  Quit")
    
        command = input("Enter command> ")
        print()
        if command == "1":
            list_users()
            print()
        elif command == "2":
            username = input("Username> ")
            password = input("Password> ")
            full_name = input("Full name> ")
            add_user(username,password,full_name)
            print()
        elif command == "3":
            username = input("Username to edit> ")
            password = input("New password (press enter to keep current)> ")
            full_name = input("full name (press enter to keep current)> ")
            edit_user(username,password,full_name)
            print()
        elif command == "4":
            username = input("enter username to delete> ")
            answer = input("Are you sure that you want to delete "+username+"?  y/n: ") 
            if answer.lower() == "y":
                print("Deleted.")
                delete_user(username)
            print()
        elif command == "5":
            quit_menu()
            print()
            break
        else: 
            print("Invalid command entered, try again; if you dare.")

if __name__ == '__main__':
    main()