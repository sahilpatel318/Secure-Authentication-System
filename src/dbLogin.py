# haslib is used for generating hashes
import hashlib

# os is used to generate a cryptographically strong salt. Alternative: secrets
from os import urandom

# b64encode is used to convert the random 32 byte salt to a
# 32 byte utf-8 string for storage in string format
from base64 import b64encode

# pandas is used to give the option of working with csv files
import pandas as pd

class Dblogin:

    # The user's password is hashed and is never stored as plain text.
    # Note: This object uses the salt as a byte-like object.
    # But for real use case a normal 32 byte string would be used
    def __init__(self, username, password):
        self.username = username
        self.password = hashlib.sha256(password.encode('utf-8')).hexdigest()
        self.salt = None

    '''
    Description: This function is to be called once database connection
                has been made and there is a record with matching username.
    @param dbPassword: The salted password stored retrieved from the database.
    @param salt: The salt retrieved from the database.
    @returns boolean: True if the credentials match, else False.
    '''

    def verify(self, dbPassword, salt):

        # Hashing the password user entered with the salt from the database
        saltedPassword = hashlib.pbkdf2_hmac('sha256',
                                             self.password.encode('utf-8'),
                                             salt,
                                             100000).hex()#[:64]

        if (dbPassword == saltedPassword):
            return True
        else:
            return False

    '''
    Description: This function uses string formatting & parameterized
                queries to safely query a database via the cursor.
    @param cursor: A pymysql (or similar) connection cursor object
                used for connecting to the SQL database.
    @param tableName: A string representing the table name where
                login data is stored.
    @param usernameCol: A string representing the column name where
                the username is stored.
    @param passwordCol: A string representing the column name where
                the salted password is stored.
    @param saltCol: A string representing the column name where
                the salt is stored.
    @returns boolean: True if the credentials match, else False.
    '''

    def sqlVerification(self, cursor,
                        tableName="login",
                        usernameCol="username",
                        passwordCol="password",
                        saltCol="salt"):

        # Parameterized Query (safeguard against SQL Injection)
        # Note: tableName and usernameCol arn't entered by the user
        query = f"SELECT {passwordCol}, {saltCol} FROM {tableName} WHERE {usernameCol} = %s"
        cursor.execute(query, (self.username,))

        # Fetch the rows (Ideally there's only 1 row)
        records = cursor.fetchall()
        # If such a column was found in the database
        if (records != ()):
            if (len(records) == 1):
                if self.verify(records[0][0],
                               records[0][1].encode('utf-8')):
                    return True

        return False

    '''
    Description: This function provides an easy way to verify credentials
                using CSV files
    @param filePath: A string representing the path to the CSV file.
    @param usernameCol: A string representing the column name where
                the username is stored.
    @param passwordCol: A string representing the column name where
                the salted password is stored.
    @param saltCol: A string representing the column name where
                the salt is stored.
    @returns boolean: True if the credentials match, else False.
    '''

    def csvVerification(self, filePath,
                        usernameCol="username",
                        passwordCol="password",
                        saltCol="salt"):

        df = pd.read_csv(filePath)
        row = df.loc[df[usernameCol] == self.username]

        if (len(row) == 1):
            if self.verify(row[passwordCol].iloc[0],
                           row[saltCol].iloc[0].encode('utf-8')):
                return True

        return False

    '''
    Description: This function is used for updating the current salt
                and returning the new salted password.
    @param strSalt: This is a flag (False by default).
                If True, the salt generated has bytes that
                can be decoded to utf-8.
                If False, the random salt generated has random
                bytes which can't be decoded to utf-8.
    @returns 2 values: salted password, salt
    '''

    def setCredentials(self):

        # 32 Random cryptografically safe bytes
        '''
        The 32 randombytes from urandom are encoded in base64
        to remove any non utf-8 bytes. Having utf-8 bytes might
        sound less secure but this makes it easier to store and
        work with the byte-like object while keeping it just as
        randomized.
        '''
        self.salt = b64encode(urandom(64))[:64]

        saltedPassword = hashlib.pbkdf2_hmac('sha256',
                                             self.password.encode('utf-8'),
                                             self.salt,
                                             100000).hex()#[:64]
        return saltedPassword, self.salt

    '''
    Description: This function is used for updating the current salt
                and returning the new salted password.
    @param cursor: A pymysql (or similar) connection cursor object
                used for connecting to the SQL database.
    @param tableName: A string representing the table name where
                login data is stored.
    @param usernameCol: A string representing the column name where
                the username is stored.
    @param passwordCol: A string representing the column name where
                the salted password is stored.
    @param saltCol: A string representing the column name where
                the salt is stored.
    @returns 2 values: salted password, salt
    '''

    def setSqlCredentials(self, cursor,
                          tableName="login",
                          usernameCol="username",
                          passwordCol="password",
                          saltCol="salt"):

        saltedPassword = self.setCredentials()[0]

        # Parameterized Query (safeguard against SQL Injection)
        # table and column identifiers are SQL safe
        query = f"SELECT * FROM {tableName} WHERE {usernameCol} = %s"
        cursor.execute(query, (self.username,))
        records = cursor.fetchall()

        if (len(records) < 2):
            if (len(records) == 1):

                # table/column identifiers and salts are SQL safe
                query = f"UPDATE {tableName} SET \
                        {passwordCol} = '{saltedPassword}', \
                        {saltCol} = '{self.salt.decode('utf-8')}' \
                        WHERE {usernameCol} = %s"
                cursor.execute(query, (self.username,))

            else:
                query = f"INSERT INTO \
                        {tableName}({usernameCol}, {passwordCol}, {saltCol}) \
                        VALUES \
                        (%s, '{saltedPassword}', '{self.salt.decode('utf-8')}')"

                cursor.execute(query, (self.username,))
        else:
            self.salt=None
            return None, None

        return saltedPassword, self.salt

    '''
    Description: This function is used for updating the current salt
                and returning the new salted password.
    @param cursor: A pymysql (or similar) connection cursor object
                used for connecting to the SQL database.
    @param tableName: A string representing the table name where
                login data is stored.
    @param usernameCol: A string representing the column name where
                the username is stored.
    @param passwordCol: A string representing the column name where
                the salted password is stored.
    @param saltCol: A string representing the column name where
                the salt is stored.
    @returns 2 values: salted password, salt
    Returns None, None if more than 1 columns match the username
    '''

    def setCsvCredentials(self, filePath,
                          usernameCol="username"):

        saltedPassword = self.setCredentials()[0]

        df = pd.read_csv(filePath)
        row = df.loc[df[usernameCol] == self.username]

        '''
        For CSV files it is assumed only 3 columns exist.
        And the data is stored as username, password and salt respectively
        '''
        if (len(row) == 0):
            df.loc[len(df)] = [self.username, saltedPassword,
                               self.salt.decode('utf-8')]

        elif (len(row) == 1):
            df.loc[df[usernameCol] == self.username] = [
                self.username, saltedPassword, self.salt.decode('utf-8')]
        else:
            self.salt = None
            return None, None

        df.to_csv(filePath, index=False)

        return saltedPassword, self.salt
