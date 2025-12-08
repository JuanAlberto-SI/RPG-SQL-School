-- =====================================================
-- Retro RPG - SCRIPT FINAL (PROYECTO COMPLETO)
-- =====================================================
USE master;
GO

IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = 'RetroRPG')
BEGIN
    CREATE DATABASE RetroRPG;
END
GO

USE RetroRPG;
GO

-- 1. TABLAS PRINCIPALES
-- ---------------------
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[Elements]') AND type in (N'U'))
BEGIN
    CREATE TABLE [dbo].[Elements] (
        [ElementID] INT IDENTITY(1,1) PRIMARY KEY,
        [ElementName] VARCHAR(50) NOT NULL UNIQUE,
        [Description] VARCHAR(255) NULL
    );
END
GO

IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[Players]') AND type in (N'U'))
BEGIN
    CREATE TABLE [dbo].[Players] (
        [PlayerID] INT IDENTITY(1,1) PRIMARY KEY,
        [Username] VARCHAR(50) NOT NULL UNIQUE,
        [PasswordHash] VARCHAR(255) NOT NULL,
        [Email] VARCHAR(100) NULL,
        [CreatedDate] DATETIME2 DEFAULT GETDATE()
    );
END
GO

IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[SaveGames]') AND type in (N'U'))
BEGIN
    CREATE TABLE [dbo].[SaveGames] (
        [SaveGameID] INT IDENTITY(1,1) PRIMARY KEY,
        [PlayerID] INT NOT NULL FOREIGN KEY REFERENCES [dbo].[Players]([PlayerID]),
        [Level] INT DEFAULT 1,
        [ExperiencePoints] INT DEFAULT 0,
        [CurrentHP] INT NOT NULL,
        [MaxHP] INT NOT NULL,
        [PositionX] DECIMAL(10,2) DEFAULT 0.0,
        [PositionY] DECIMAL(10,2) DEFAULT 0.0,
        [PositionZ] DECIMAL(10,2) DEFAULT 1.0, -- Usado para guardar el NIVEL DESBLOQUEADO
        [LastSaved] DATETIME2 DEFAULT GETDATE()
    );
END
GO

IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[MonsterCatalog]') AND type in (N'U'))
BEGIN
    CREATE TABLE [dbo].[MonsterCatalog] (
        [MonsterID] INT IDENTITY(1,1) PRIMARY KEY,
        [MonsterName] VARCHAR(100) NOT NULL,
        [ElementID] INT NOT NULL,
        [BaseHP] INT NOT NULL,
        [BaseAttack] INT NOT NULL,
        [BaseDefense] INT NOT NULL,
        [BaseSpeed] INT NOT NULL,
        [Description] VARCHAR(500) NULL
    );
END
GO

-- 2. DATOS INICIALES (AQUI ESTA LA CLAVE)
-- ---------------------------------------

-- Elementos
IF NOT EXISTS (SELECT * FROM Elements WHERE ElementName = 'Fire') INSERT INTO Elements VALUES ('Fire', 'Fuego');
IF NOT EXISTS (SELECT * FROM Elements WHERE ElementName = 'Water') INSERT INTO Elements VALUES ('Water', 'Agua');
IF NOT EXISTS (SELECT * FROM Elements WHERE ElementName = 'Plant') INSERT INTO Elements VALUES ('Plant', 'Planta');

-- MONSTRUOS (Borramos los viejos para asegurar que esten los del juego)
DELETE FROM MonsterCatalog;

-- Insertamos los que usa el juego (Goblin, Brain, Shadow, Ogre)
INSERT INTO MonsterCatalog (MonsterName, ElementID, BaseHP, BaseAttack, BaseDefense, BaseSpeed, Description)
VALUES 
('Goblin', 3, 30, 5, 2, 2, 'Un habitante basico del bosque.'),
('Brain', 2, 20, 10, 0, 4, 'Enemigo psiquico que dispara energia.'),
('Shadow', 1, 50, 15, 5, 3, 'Se teletransporta y ataca rapido.'),
('Ogre', 1, 150, 25, 10, 1, 'El Jefe Final. Lento pero mortal.');

PRINT 'Base de datos actualizada con los monstruos correctos.';
GO

-- 3. CONSULTA DE DEMOSTRACIÓN (Para el Profesor)
-- Copia y pega esto en una Nueva Consulta para enseñar el avance
/*
SELECT 
    P.Username AS [Heroe], 
    S.Level AS [Nivel], 
    CAST(S.PositionZ AS INT) AS [Mapa Desbloqueado], 
    S.ExperiencePoints AS [XP], 
    S.CurrentHP AS [Vida], 
    S.LastSaved AS [Ultimo Guardado]
FROM SaveGames S
INNER JOIN Players P ON S.PlayerID = P.PlayerID
WHERE P.Username = 'Player1';
*/