-- =====================================================
-- Retro RPG - SCRIPT DE REINICIO TOTAL (SOLUCION FINAL)
-- =====================================================
USE master;
GO

-- 1. SI EXISTE LA BASE DE DATOS, LA BORRAMOS (KICKEO A TODOS)
IF EXISTS (SELECT * FROM sys.databases WHERE name = 'RetroRPG')
BEGIN
    -- Esto cierra todas las conexiones abiertas para poder borrarla
    ALTER DATABASE RetroRPG SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE RetroRPG;
    PRINT 'Base de datos vieja eliminada.';
END
GO

-- 2. CREAMOS LA NUEVA LIMPIA
CREATE DATABASE RetroRPG;
GO

USE RetroRPG;
GO

-- =====================================================
-- CREACIÓN DE TABLAS (ESTRUCTURA NUEVA Y LIMPIA)
-- =====================================================

-- TABLA ELEMENTOS
CREATE TABLE [dbo].[Elements] (
    [ElementID] INT IDENTITY(1,1) PRIMARY KEY,
    [ElementName] VARCHAR(50) NOT NULL UNIQUE,
    [Description] VARCHAR(255) NULL
);
GO

-- TABLA JUGADORES
CREATE TABLE [dbo].[Players] (
    [PlayerID] INT IDENTITY(1,1) PRIMARY KEY,
    [Username] VARCHAR(50) NOT NULL UNIQUE,
    [PasswordHash] VARCHAR(255) NOT NULL,
    [Email] VARCHAR(100) NULL,
    [CreatedDate] DATETIME2 DEFAULT GETDATE()
);
GO

-- TABLA PARTIDAS GUARDADAS
CREATE TABLE [dbo].[SaveGames] (
    [SaveGameID] INT IDENTITY(1,1) PRIMARY KEY,
    [PlayerID] INT NOT NULL FOREIGN KEY REFERENCES [dbo].[Players]([PlayerID]),
    [Level] INT DEFAULT 1,
    [ExperiencePoints] INT DEFAULT 0,
    [CurrentHP] INT NOT NULL,
    [MaxHP] INT NOT NULL,
    [PositionX] DECIMAL(10,2) DEFAULT 0.0,
    [PositionY] DECIMAL(10,2) DEFAULT 0.0,
    [PositionZ] DECIMAL(10,2) DEFAULT 1.0, -- Mapa Desbloqueado
    [LastSaved] DATETIME2 DEFAULT GETDATE()
);
GO

-- TABLA MONSTRUOS
CREATE TABLE [dbo].[MonsterCatalog] (
    [MonsterID] INT IDENTITY(1,1) PRIMARY KEY,
    [MonsterName] VARCHAR(100) NOT NULL,
    [ElementID] INT NOT NULL, -- FK Manual (Simulada para simplificar)
    [BaseHP] INT NOT NULL,
    [BaseAttack] INT NOT NULL,
    [BaseDefense] INT NOT NULL,
    [BaseSpeed] INT NOT NULL,
    [Description] VARCHAR(500) NULL
);
GO

-- =====================================================
-- INSERCIÓN DE DATOS (SEEDING)
-- =====================================================

PRINT 'Insertando datos...';

-- Elementos (Especificando columnas para evitar error 213)
INSERT INTO [dbo].[Elements] (ElementName, Description) VALUES 
('Fire', 'Fuego'),
('Water', 'Agua'),
('Plant', 'Planta');

-- Monstruos (Los exactos que usa tu juego)
INSERT INTO [dbo].[MonsterCatalog] (MonsterName, ElementID, BaseHP, BaseAttack, BaseDefense, BaseSpeed, Description)
VALUES 
('Goblin', 3, 30, 5, 2, 2, 'Un habitante basico del bosque.'),
('Brain', 2, 20, 10, 0, 4, 'Enemigo psiquico que dispara energia.'),
('Shadow', 1, 50, 15, 5, 3, 'Se teletransporta y ataca rapido.'),
('Ogre', 1, 150, 25, 10, 1, 'El Jefe Final. Lento pero mortal.');

PRINT '===========================================';
PRINT '¡BASE DE DATOS REPARADA Y LISTA!';
PRINT '===========================================';
GO