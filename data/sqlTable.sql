// Full Name  : Sahil Hareshbhai Patel
// -----------------------------------------------------------


CREATE TABLE loginInfo(
    loginid int AUTO_INCREMENT,
    username VARCHAR(255) NOT NULL,
    password CHAR(64) NOT NULL,
    salt CHAR(64),
    PRIMARY KEY(loginid)
);
