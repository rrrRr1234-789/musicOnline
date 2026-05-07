CREATE DATABASE IF NOT EXISTS musicOnline;
USE musicOnline;

CREATE TABLE publicUsers (
    userID INT PRIMARY KEY AUTO_INCREMENT,
    firstName VARCHAR(50) NOT NULL,
    surname VARCHAR(50) NOT NULL,
    email VARCHAR(120) NOT NULL UNIQUE,
    phoneNo VARCHAR(20),
    password VARCHAR(255) NOT NULL,
    salt VARCHAR(255),
    dateRegistered DATE NOT NULL DEFAULT (CURRENT_DATE)
);

CREATE TABLE admin (
    adminID INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(120) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(30) NOT NULL,
    dateCreated DATE NOT NULL DEFAULT (CURRENT_DATE)
);

CREATE TABLE vinyls (
    id INT PRIMARY KEY AUTO_INCREMENT,
    artist VARCHAR(100) NOT NULL,
    album VARCHAR(150) NOT NULL,
    recordType VARCHAR(20) NOT NULL,
    releaseDate DATE,
    year YEAR,
    genre VARCHAR(50),
    `condition` VARCHAR(50),
    price DECIMAL(8,2) NOT NULL,
    description TEXT,
    albumCover VARCHAR(255),
    status VARCHAR(30) NOT NULL DEFAULT 'Visible',
    dateAdded DATE NOT NULL DEFAULT (CURRENT_DATE),
    userID INT NOT NULL,
    FOREIGN KEY (userID) REFERENCES publicUsers(userID)
);
