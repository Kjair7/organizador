-- Scripts SQL para crear las tablas de la base de datos
-- Ejecutar estos scripts en phpMyAdmin o en la consola de MySQL

-- Crear la base de datos si no existe
CREATE DATABASE IF NOT EXISTS organizador;
USE organizador;

-- Creación de la tabla Usuarios
-- Almacena información de usuarios para autenticación y recuperación de contraseña
CREATE TABLE IF NOT EXISTS Usuarios (
    id_usuario INTEGER PRIMARY KEY AUTO_INCREMENT, -- Clave primaria con incremento automático (MySQL)
    nombre_usuario VARCHAR(255) NOT NULL UNIQUE, -- Nombre de usuario único
    cedula VARCHAR(50) NOT NULL UNIQUE, -- Cédula única para identificación
    correo_electronico VARCHAR(255) NOT NULL UNIQUE, -- Correo único para login y recuperación
    contrasena_hash VARCHAR(255) NOT NULL, -- Contraseña hasheada
    fecha_registro DATE NOT NULL -- Fecha de registro (formato 'YYYY-MM-DD')
);

-- Creación de la tabla Historial
-- Registra acciones de 'organizar' y 'eliminar_carpetas'
CREATE TABLE IF NOT EXISTS Historial (
    id_accion INTEGER PRIMARY KEY AUTO_INCREMENT, -- Clave primaria
    id_usuario INTEGER NOT NULL, -- Referencia al usuario
    tipo ENUM('organizar', 'eliminar_carpetas') NOT NULL, -- Tipo de acción restringido
    fecha DATETIME NOT NULL, -- Fecha y hora en formato 'YYYY-MM-DD HH:MM:SS'
    detalle TEXT, -- Detalles en JSON (ej. '{"accion": "organizar_basica", "archivos_movidos": 10}')
    ruta_cuarentena TEXT, -- Ruta para restauración (puede ser NULL)
    FOREIGN KEY (id_usuario) REFERENCES Usuarios(id_usuario) ON DELETE CASCADE
);

-- Creación de la tabla Reglas
-- Almacena reglas de clasificación personalizadas
CREATE TABLE IF NOT EXISTS Reglas (
    id_regla INTEGER PRIMARY KEY AUTO_INCREMENT, -- Clave primaria
    id_usuario INTEGER NOT NULL, -- Referencia al usuario
    nombre VARCHAR(255) NOT NULL, -- Nombre de la regla (ej. 'Documentos PDF')
    destino_subcarpeta VARCHAR(255) NOT NULL, -- Subcarpeta de destino (ej. 'Documentos')
    extensiones TEXT, -- Extensiones en JSON (ej. '["pdf", "docx"]')
    tam_min_kb INTEGER, -- Tamaño mínimo en KB (puede ser NULL)
    tam_max_kb INTEGER, -- Tamaño máximo en KB (puede ser NULL)
    fecha_desde DATE, -- Fecha mínima (puede ser NULL)
    fecha_hasta DATE, -- Fecha máxima (puede ser NULL)
    FOREIGN KEY (id_usuario) REFERENCES Usuarios(id_usuario) ON DELETE CASCADE
);

-- Creación de la tabla Configuraciones
-- Almacena configuraciones como cambios de nombre de usuario, contraseña y exclusiones
CREATE TABLE IF NOT EXISTS Configuraciones (
    id_config INTEGER PRIMARY KEY AUTO_INCREMENT, -- Clave primaria
    id_usuario INTEGER NOT NULL, -- Referencia al usuario
    clave VARCHAR(255) NOT NULL, -- Nombre de la configuración (ej. 'nombre_usuario_nuevo', 'exclusiones_vacias')
    valor TEXT NOT NULL, -- Valor de la configuración (ej. JSON o texto)
    fecha_modificacion DATETIME NOT NULL, -- Fecha de modificación (formato 'YYYY-MM-DD HH:MM:SS')
    FOREIGN KEY (id_usuario) REFERENCES Usuarios(id_usuario) ON DELETE CASCADE,
    UNIQUE KEY unique_user_key (id_usuario, clave)
);

-- Crear índices para mejorar el rendimiento
CREATE INDEX idx_usuarios_email ON Usuarios(correo_electronico);
CREATE INDEX idx_usuarios_cedula ON Usuarios(cedula);
CREATE INDEX idx_historial_usuario ON Historial(id_usuario);
CREATE INDEX idx_historial_fecha ON Historial(fecha);
CREATE INDEX idx_reglas_usuario ON Reglas(id_usuario);
CREATE INDEX idx_configuraciones_usuario ON Configuraciones(id_usuario);


