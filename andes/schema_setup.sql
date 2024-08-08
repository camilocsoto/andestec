-- schema_setup.sql

-- PostgreSQL Script for Production

-- Crear el esquema si no existe
CREATE SCHEMA IF NOT EXISTS Andes_Tec_db;

-- Usar el esquema
SET search_path TO Andes_Tec_db;

-- Crear tabla user
CREATE TABLE IF NOT EXISTS Andes_Tec_db."user" (
  us_id SERIAL PRIMARY KEY,
  us_name VARCHAR(75),
  us_contact VARCHAR(15),
  us_mail VARCHAR(95),
  us_hash_pass TEXT,
  us_status BYTEA DEFAULT E'\\x01'
);

-- Crear tabla sensors
CREATE TABLE IF NOT EXISTS Andes_Tec_db.sensors (
  sen_id SERIAL PRIMARY KEY,
  sen_name VARCHAR(85),
  sen_type VARCHAR(45),
  max_capacity INT,
  sen_serialNo VARCHAR(45),
  sen_imei VARCHAR(45),
  user_us_id INT NOT NULL,
  FOREIGN KEY (user_us_id) REFERENCES Andes_Tec_db."user" (us_id) ON DELETE CASCADE ON UPDATE CASCADE
);

-- Crear tabla variables
CREATE TABLE IF NOT EXISTS Andes_Tec_db.variables (
  var_id SERIAL PRIMARY KEY,
  var_temperature DECIMAL,
  var_radiofrecuency INT,
  var_presure DECIMAL,
  var_force INT,
  var_capacity INT,
  var_battery INT,
  sensors_sen_id INT NOT NULL,
  localizacion TEXT,
  FOREIGN KEY (sensors_sen_id) REFERENCES Andes_Tec_db.sensors (sen_id) ON DELETE CASCADE ON UPDATE CASCADE
);
