
# Secure Authentication/Login System

Hey there! This repo contains the **dbLogin** module. The DbLogin class can manage and work with login credentials without worrying about hashing and salting yourself.

The project was originally started a few months ago as a part of a web-based portal for database management. However, due to personal circumstances, it was halted.

# Table of Contents

-  [Files](https://github.com/KaosElegent/database-login-system/tree/main#files)

-  [Why Salt and Hash?](https://github.com/KaosElegent/database-login-system/tree/main#why-salt-and-hash) 
   - [Normal Password Storage](https://github.com/KaosElegent/database-login-system/tree/main#normal-password-storage)
   - [Hashed Password Storage](https://github.com/KaosElegent/database-login-system/tree/main#hashed-password-storage-sha-256)
   - [Salted & Hashed Password Storage](https://github.com/KaosElegent/database-login-system/tree/main#salted--hashed-password-storage)

- [Implementation](#implementation)
  - [Create or Update an Existing User](https://github.com/KaosElegent/database-login-system/tree/main#create-or-update-an-existing-user-)
  - [Authenticate an Existing User](https://github.com/KaosElegent/database-login-system/tree/main#authenticate-an-existing-user-)

- [Working Demo](https://github.com/KaosElegent/database-login-system/tree/main#working-demo)

- [Notes](https://github.com/KaosElegent/database-login-system/tree/main#notes)

# Files

- **src/main.py** (Demo file to showcase the **DbLogin** class)
- **src/dblogin.py** (The DbLogin source file)
- **data/login.csv** (The CSV file used for the Demo)
- **data/sqlDatabase.sql** (The table structure used for querying)

# Why Salt and Hash?

This system can be used wherever password-based authentication is required.
### Normal password storage:

|Username|Password|
|-|-|
|User1|123456|
|User2|abcdefg123|
|User3|123user3|
|User4|123456|

### Hashed password storage (SHA-256):

|Username|Password|
|-|-|
|User1|8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92|
|User2|200f5183a8d9ef5339eaf6e3987d892e8751036beaa158257c1b65d78e3fa0f2|
|User3|a739cb1f52c35fd553252198fc98cee2135e1dc912f6dd640d0a667f4981fd80|
|User4|8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92|
 
#### Issues with this system
1) **User1** and **User4** have the same hash.
2) If the attacker has a hash list of the most common passwords, this makes the hashing process pointless.

> Note:
> While hashing the password is one-way and the original password isn't leaked, users with the same passwords (commonly used passwords) have the same hash, which makes it easy for the infiltrator to get everyone's credentials.

### Salted & Hashed password storage:

|Username|Password|Salt|
|-|-|-|
User1|411ac76c94b5587606b0314ddbfb2951cecc2278b85f14641f41f9092ac148e7|RCz7jheLX4mt+RZcRhf4IlOe+d9az0vMVQLnEMI1NV3lhO/v5Bdzd+FHf1fBfPHn
User2|db06d70ddd2d8b2fe981d9a56cb48ec2b9f227e9d79a05a56aeea8462e840bb0|2VvbCB7ix1RB2Es/kKKQzWLPqGIsTQZ+57C7yjdIpv5d+DjJEuApblgAJy3kNd+P
User3|c04acda7dbf4a5191fd2402c864313f9fbdeab6ef44913740692868902ceaaff|YHeYd9En6pV4N2kYEA6dh95ph7cSFoldTEHeaCiQn7Z8V5PxKtH8s8cMBxq6wDs9
User4|1ee2071b7009061186e640000f41f535af617f30b5e8305196df96c276cf1552|2C5eEgPe02O7/33x1at3hV5PyA2X+ogxP3A4egx44b79uzzTHYWcJnhX3yPAPrgB

Now, the users with the same original passwords have a uniquely hashed password since we added a salt during the hashing process. This 64-byte UTF-8 decoded salt is randomly generated and is used to hash the original hashed password (100,000 times in the **DbLogin** system, before storage).

This renders hash lists completely useless and the attacker now has to spend a lot of time on every user's credentials.

# Implementation

### Create or Update an existing user :
New credentials (salt and a salted + hashed password) are created and stored.

1) A 64-byte cryptographically secure pseudorandom salt is generated (using urandom)
2) This salt is then encoded to UTF-8 using base64. This is because it is unlikely that a random byte can be decoded as UTF-8. Which means storing and displaying it would be harder.
3) A salted password is generated via 100,000 rounds of SHA-256 hashing using the user-entered password hash and the generated salt. This hashing uses PKCS#5 password-based key derivation function and HMAC (for pseudorandomness).


### Authenticate an existing user :
The username and password (which gets hashed as soon as possible) are taken from the user. After which the password entered by the user is hashed using the salt from the database and cross-referenced with the stored credentials.

1) Once the user enters their password, it is overwritten with its SHA-256 hash and stored as an attribute.
2) A salted password is then generated via 100,000 rounds of SHA-256 hashing using the user-entered password hash and the salt retrieved from the database. This hashing uses PKCS#5 password-based key derivation function and HMAC (for pseudorandomness).
3) This salted password is then compared with the password retrieved from the database for authentication.

> Note:
> The above actions are also performed for CSV files using Pandas library, and SQL databases using MySQL library.

# Working Demo


- **The main menu :**

![Main Menu](https://github.com/KaosElegent/database-login-system/blob/main/images/mainMenu.png?raw=true)

- **User creation :**

![User Creation](https://github.com/KaosElegent/database-login-system/blob/main/images/addUser.png?raw=true)

- **User credentials updated :**

![User Updated](https://github.com/KaosElegent/database-login-system/blob/main/images/updateUser.png?raw=true)

- **Invalid user credentials :**

![Invalid Credentials](https://github.com/KaosElegent/database-login-system/blob/main/images/invalidLogin.png?raw=true)

- **Valid user credentials :**

![Valid Credentials](https://github.com/KaosElegent/database-login-system/blob/main/images/login.png?raw=true)  

# Notes

- This project assumes that the password and salt are stored in separate columns.
- The DbLogin functions will return invalid authentication/credentials if more than 1 record has the same required username.
- The CSV-based functions assume that the file only contains 3 columns (username, password, salt)
