# ----------- For using a MySQL Database -----------

from dbLogin import Dblogin  # For using the custom class

# To connect to a MySQL database
import mysql.connector

# To use environment variables
import os
from dotenv import load_dotenv
load_dotenv()

# --------------------------------------------------


# The database connection object
connection = mysql.connector.connect(host=os.getenv("DATABASE_HOST"),
                                     user=os.getenv("DATABASE_USERNAME"),
                                     password=os.getenv("DATABASE_PASSWORD"),
                                     database=os.getenv("DATABASE"),
                                     autocommit=True)
cursor = connection.cursor()


def login(csvFile):
    details = Dblogin(input("Username: "), input("Password: "))

    if (csvFile):
        if details.csvVerification(filePath=os.path.join("..","data", "login.csv")):
            print("Login Successful!\n")
        else:
            print("Invalid Credentials!\n")
    else:
        if details.sqlVerification(cursor=cursor, tableName="loginInfo",):
            print("Login Successful!\n")
        else:
            print("Invalid Credentials!\n")


def alter(csvFile):
    while (True):
        details = Dblogin(input("Username: "), input("Password: "))
        if (input("Confirm? (y/n)").lower() == 'y'):
            break
        else:
            return

    if (csvFile):
        if details.setCsvCredentials(filePath=os.path.join("..","data", "login.csv"))[1]:
            print("Credentials Updated/Added Successfully!")
        else:
            print("There was a system error!")
    else:
        if details.setSqlCredentials(cursor=cursor, tableName="loginInfo")[1]:
            print("Credentials Altered Successfully!")
        else:
            print("There was a system error! Multiple Users with same username!")


def menu():
    while True:
        print(
            """
----------------------------------------------------
                     Main Menu                       
----------------------------------------------------
1) Use a CSV File
2) Use a SQL Database
0) Exit
""")
        fileType = input("> ")
        if fileType in ['1', '2']:
            while True:
                print(
                    """
----------------------------------------------------
                Working with Credentials             
----------------------------------------------------
1) Login
2) Add/Update User
0) Go Back (Main Menu)
""")
                taskType = input("> ")
                if taskType == '1':
                    if fileType == '1':
                        login(csvFile=True)
                    else:
                        login(csvFile=False)
                elif taskType == '2':
                    if fileType == '1':
                        alter(csvFile=True)
                    else:
                        alter(csvFile=False)
                elif taskType == '0':
                    break
                else:
                    print("Invalid Input!\n")

        elif fileType == '0':
            break
        else:
            print("Invalid Input!\n")

    cursor.close()
    print("\n-------------------------------\nThank you for using the System!\n-------------------------------")


if __name__ == '__main__':
    menu()
