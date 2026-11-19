-- Crea la base de datos y el usuario de Cartaviva en MySQL 8.
-- Ejecutar una sola vez como root (MySQL Workbench o la consola de XAMPP):
--   mysql -u root -p < docs/mysql/crear_bd.sql
-- Antes de ejecutarlo, cambia la contraseña de abajo y pon la misma en DB_PASSWORD del .env

CREATE DATABASE IF NOT EXISTS cartaviva
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

CREATE USER IF NOT EXISTS 'cartaviva'@'localhost' IDENTIFIED BY 'cambia-esta-clave';

-- Permisos solo sobre la base del proyecto, no sobre todo el servidor.
GRANT ALL PRIVILEGES ON cartaviva.* TO 'cartaviva'@'localhost';

-- pytest crea una base temporal llamada test_cartaviva y la borra al terminar.
GRANT ALL PRIVILEGES ON test_cartaviva.* TO 'cartaviva'@'localhost';

FLUSH PRIVILEGES;
