-- Crear la base de datos
CREATE DATABASE IF NOT EXISTS contact_db;
USE contact_db;

-- Crear la tabla contacts con el campo profile_image
CREATE TABLE IF NOT EXISTS contacts (
    id INT AUTO_INCREMENT PRIMARY KEY,          -- Identificador único del contacto
    name VARCHAR(100) NOT NULL,                 -- Nombre del contacto (obligatorio)
    phone VARCHAR(20) NOT NULL,                 -- Teléfono del contacto (obligatorio, solo números)
    email VARCHAR(100),                         -- Correo electrónico del contacto (opcional)
    profile_image VARCHAR(255)                  -- Ruta de la imagen de perfil (opcional)
);