-- Employee Directory schema (MySQL 8+)
-- The app also creates this table automatically on startup via SQLAlchemy;
-- this file documents the design and can be run manually.

CREATE DATABASE IF NOT EXISTS employee_directory
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE employee_directory;

CREATE TABLE IF NOT EXISTS employees (
  id              INT          NOT NULL AUTO_INCREMENT,
  name            VARCHAR(100) NOT NULL,
  email           VARCHAR(150) NOT NULL,
  department      VARCHAR(100) NOT NULL,
  designation     VARCHAR(100) NOT NULL,
  date_of_joining DATE         NOT NULL,

  PRIMARY KEY (id),
  UNIQUE KEY uq_employees_email (email),   -- no duplicate employees; fast lookup by email
  KEY ix_employees_name (name),            -- prefix search: name LIKE 'rah%' + ORDER BY name
  KEY ix_employees_department (department) -- prefix search: department LIKE 'eng%'
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_unicode_ci;              -- case-insensitive LIKE without LOWER(), so indexes stay usable
