-- =====================================================
-- Retro RPG Game Database Setup Script
-- SQL Server T-SQL Script
-- =====================================================
-- Description: Creates database schema for Retro RPG game
-- Idempotent: Can be safely re-run multiple times
-- =====================================================

USE master;
GO

-- Create database if it doesn't exist
IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = 'RetroRPG')
BEGIN
    CREATE DATABASE RetroRPG;
    PRINT 'Database RetroRPG created successfully.';
END
ELSE
BEGIN
    PRINT 'Database RetroRPG already exists.';
END
GO

USE RetroRPG;
GO

-- =====================================================
-- TABLE: Elements
-- Purpose: Defines elemental types (Fire, Water, Plant)
-- =====================================================
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[Elements]') AND type in (N'U'))
BEGIN
    CREATE TABLE [dbo].[Elements] (
        [ElementID] INT IDENTITY(1,1) NOT NULL,
        [ElementName] VARCHAR(50) NOT NULL,
        [Description] VARCHAR(255) NULL,
        [CreatedDate] DATETIME2 DEFAULT GETDATE() NOT NULL,
        CONSTRAINT [PK_Elements] PRIMARY KEY CLUSTERED ([ElementID] ASC),
        CONSTRAINT [UQ_Elements_ElementName] UNIQUE ([ElementName])
    );
    PRINT 'Table Elements created successfully.';
END
ELSE
BEGIN
    PRINT 'Table Elements already exists.';
END
GO

-- =====================================================
-- TABLE: Players
-- Purpose: Stores player login credentials and account info
-- =====================================================
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[Players]') AND type in (N'U'))
BEGIN
    CREATE TABLE [dbo].[Players] (
        [PlayerID] INT IDENTITY(1,1) NOT NULL,
        [Username] VARCHAR(50) NOT NULL,
        [PasswordHash] VARCHAR(255) NOT NULL,
        [Email] VARCHAR(100) NULL,
        [CreatedDate] DATETIME2 DEFAULT GETDATE() NOT NULL,
        [LastLoginDate] DATETIME2 NULL,
        [IsActive] BIT DEFAULT 1 NOT NULL,
        CONSTRAINT [PK_Players] PRIMARY KEY CLUSTERED ([PlayerID] ASC),
        CONSTRAINT [UQ_Players_Username] UNIQUE ([Username]),
        CONSTRAINT [UQ_Players_Email] UNIQUE ([Email])
    );
    PRINT 'Table Players created successfully.';
END
ELSE
BEGIN
    PRINT 'Table Players already exists.';
END
GO

-- =====================================================
-- TABLE: MonsterCatalog
-- Purpose: Defines all available monsters with base stats
-- =====================================================
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[MonsterCatalog]') AND type in (N'U'))
BEGIN
    CREATE TABLE [dbo].[MonsterCatalog] (
        [MonsterID] INT IDENTITY(1,1) NOT NULL,
        [MonsterName] VARCHAR(100) NOT NULL,
        [ElementID] INT NOT NULL,
        [BaseHP] INT NOT NULL,
        [BaseAttack] INT NOT NULL,
        [BaseDefense] INT NOT NULL,
        [BaseSpeed] INT NOT NULL,
        [Description] VARCHAR(500) NULL,
        [CreatedDate] DATETIME2 DEFAULT GETDATE() NOT NULL,
        CONSTRAINT [PK_MonsterCatalog] PRIMARY KEY CLUSTERED ([MonsterID] ASC),
        CONSTRAINT [FK_MonsterCatalog_Elements] FOREIGN KEY ([ElementID]) 
            REFERENCES [dbo].[Elements] ([ElementID]) ON DELETE NO ACTION ON UPDATE CASCADE,
        CONSTRAINT [CK_MonsterCatalog_BaseHP] CHECK ([BaseHP] > 0),
        CONSTRAINT [CK_MonsterCatalog_BaseAttack] CHECK ([BaseAttack] >= 0),
        CONSTRAINT [CK_MonsterCatalog_BaseDefense] CHECK ([BaseDefense] >= 0),
        CONSTRAINT [CK_MonsterCatalog_BaseSpeed] CHECK ([BaseSpeed] >= 0)
    );
    PRINT 'Table MonsterCatalog created successfully.';
END
ELSE
BEGIN
    PRINT 'Table MonsterCatalog already exists.';
END
GO

-- =====================================================
-- TABLE: Items
-- Purpose: Defines all items available in the game
-- =====================================================
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[Items]') AND type in (N'U'))
BEGIN
    CREATE TABLE [dbo].[Items] (
        [ItemID] INT IDENTITY(1,1) NOT NULL,
        [ItemName] VARCHAR(100) NOT NULL,
        [ItemType] VARCHAR(50) NOT NULL, -- 'Weapon', 'Armor', 'Consumable', 'Quest', etc.
        [ElementID] INT NULL, -- NULL for non-elemental items
        [StatBonus] INT DEFAULT 0 NOT NULL, -- Generic stat bonus (can be HP, Attack, etc.)
        [Description] VARCHAR(500) NULL,
        [IsConsumable] BIT DEFAULT 0 NOT NULL,
        [CreatedDate] DATETIME2 DEFAULT GETDATE() NOT NULL,
        CONSTRAINT [PK_Items] PRIMARY KEY CLUSTERED ([ItemID] ASC),
        CONSTRAINT [FK_Items_Elements] FOREIGN KEY ([ElementID]) 
            REFERENCES [dbo].[Elements] ([ElementID]) ON DELETE SET NULL ON UPDATE CASCADE,
        CONSTRAINT [CK_Items_ItemType] CHECK ([ItemType] IN ('Weapon', 'Armor', 'Consumable', 'Quest', 'Other'))
    );
    PRINT 'Table Items created successfully.';
END
ELSE
BEGIN
    PRINT 'Table Items already exists.';
END
GO

-- =====================================================
-- TABLE: SaveGames
-- Purpose: Stores player save game data (Level, XP, Position)
-- =====================================================
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[SaveGames]') AND type in (N'U'))
BEGIN
    CREATE TABLE [dbo].[SaveGames] (
        [SaveGameID] INT IDENTITY(1,1) NOT NULL,
        [PlayerID] INT NOT NULL,
        [SaveName] VARCHAR(100) NULL, -- Optional save slot name
        [Level] INT DEFAULT 1 NOT NULL,
        [ExperiencePoints] INT DEFAULT 0 NOT NULL,
        [CurrentHP] INT NOT NULL,
        [MaxHP] INT NOT NULL,
        [PositionX] DECIMAL(10,2) DEFAULT 0.0 NOT NULL,
        [PositionY] DECIMAL(10,2) DEFAULT 0.0 NOT NULL,
        [PositionZ] DECIMAL(10,2) DEFAULT 0.0 NOT NULL,
        [LastSaved] DATETIME2 DEFAULT GETDATE() NOT NULL,
        [IsActive] BIT DEFAULT 1 NOT NULL,
        CONSTRAINT [PK_SaveGames] PRIMARY KEY CLUSTERED ([SaveGameID] ASC),
        CONSTRAINT [FK_SaveGames_Players] FOREIGN KEY ([PlayerID]) 
            REFERENCES [dbo].[Players] ([PlayerID]) ON DELETE CASCADE ON UPDATE CASCADE,
        CONSTRAINT [CK_SaveGames_Level] CHECK ([Level] > 0),
        CONSTRAINT [CK_SaveGames_ExperiencePoints] CHECK ([ExperiencePoints] >= 0),
        CONSTRAINT [CK_SaveGames_CurrentHP] CHECK ([CurrentHP] >= 0),
        CONSTRAINT [CK_SaveGames_MaxHP] CHECK ([MaxHP] > 0),
        CONSTRAINT [CK_SaveGames_HP_Logic] CHECK ([CurrentHP] <= [MaxHP])
    );
    PRINT 'Table SaveGames created successfully.';
END
ELSE
BEGIN
    PRINT 'Table SaveGames already exists.';
END
GO

-- =====================================================
-- TABLE: Inventory
-- Purpose: Links items to player save games (player inventory)
-- =====================================================
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[Inventory]') AND type in (N'U'))
BEGIN
    CREATE TABLE [dbo].[Inventory] (
        [InventoryID] INT IDENTITY(1,1) NOT NULL,
        [SaveGameID] INT NOT NULL,
        [ItemID] INT NOT NULL,
        [Quantity] INT DEFAULT 1 NOT NULL,
        [AcquiredDate] DATETIME2 DEFAULT GETDATE() NOT NULL,
        CONSTRAINT [PK_Inventory] PRIMARY KEY CLUSTERED ([InventoryID] ASC),
        CONSTRAINT [FK_Inventory_SaveGames] FOREIGN KEY ([SaveGameID]) 
            REFERENCES [dbo].[SaveGames] ([SaveGameID]) ON DELETE CASCADE ON UPDATE CASCADE,
        CONSTRAINT [FK_Inventory_Items] FOREIGN KEY ([ItemID]) 
            REFERENCES [dbo].[Items] ([ItemID]) ON DELETE CASCADE ON UPDATE CASCADE,
        CONSTRAINT [CK_Inventory_Quantity] CHECK ([Quantity] > 0),
        CONSTRAINT [UQ_Inventory_SaveGame_Item] UNIQUE ([SaveGameID], [ItemID]) -- One row per item per save game
    );
    PRINT 'Table Inventory created successfully.';
END
ELSE
BEGIN
    PRINT 'Table Inventory already exists.';
END
GO

-- =====================================================
-- CREATE INDEXES for Performance
-- =====================================================

-- Index on MonsterCatalog.ElementID
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_MonsterCatalog_ElementID' AND object_id = OBJECT_ID('dbo.MonsterCatalog'))
BEGIN
    CREATE NONCLUSTERED INDEX [IX_MonsterCatalog_ElementID] ON [dbo].[MonsterCatalog] ([ElementID]);
    PRINT 'Index IX_MonsterCatalog_ElementID created.';
END
GO

-- Index on Items.ElementID
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_Items_ElementID' AND object_id = OBJECT_ID('dbo.Items'))
BEGIN
    CREATE NONCLUSTERED INDEX [IX_Items_ElementID] ON [dbo].[Items] ([ElementID]);
    PRINT 'Index IX_Items_ElementID created.';
END
GO

-- Index on SaveGames.PlayerID
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_SaveGames_PlayerID' AND object_id = OBJECT_ID('dbo.SaveGames'))
BEGIN
    CREATE NONCLUSTERED INDEX [IX_SaveGames_PlayerID] ON [dbo].[SaveGames] ([PlayerID]);
    PRINT 'Index IX_SaveGames_PlayerID created.';
END
GO

-- Index on Inventory.SaveGameID
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_Inventory_SaveGameID' AND object_id = OBJECT_ID('dbo.Inventory'))
BEGIN
    CREATE NONCLUSTERED INDEX [IX_Inventory_SaveGameID] ON [dbo].[Inventory] ([SaveGameID]);
    PRINT 'Index IX_Inventory_SaveGameID created.';
END
GO

-- Index on Inventory.ItemID
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_Inventory_ItemID' AND object_id = OBJECT_ID('dbo.Inventory'))
BEGIN
    CREATE NONCLUSTERED INDEX [IX_Inventory_ItemID] ON [dbo].[Inventory] ([ItemID]);
    PRINT 'Index IX_Inventory_ItemID created.';
END
GO

-- =====================================================
-- DATA SEEDING
-- =====================================================

PRINT '';
PRINT 'Starting data seeding...';
PRINT '';

-- =====================================================
-- SEED: Elements (3 types)
-- =====================================================
IF NOT EXISTS (SELECT * FROM [dbo].[Elements] WHERE [ElementName] = 'Fire')
BEGIN
    INSERT INTO [dbo].[Elements] ([ElementName], [Description])
    VALUES ('Fire', 'The element of flame and passion. Strong against Plant, weak against Water.');
    PRINT 'Element ''Fire'' inserted.';
END
ELSE
BEGIN
    PRINT 'Element ''Fire'' already exists.';
END
GO

IF NOT EXISTS (SELECT * FROM [dbo].[Elements] WHERE [ElementName] = 'Water')
BEGIN
    INSERT INTO [dbo].[Elements] ([ElementName], [Description])
    VALUES ('Water', 'The element of flow and adaptability. Strong against Fire, weak against Plant.');
    PRINT 'Element ''Water'' inserted.';
END
ELSE
BEGIN
    PRINT 'Element ''Water'' already exists.';
END
GO

IF NOT EXISTS (SELECT * FROM [dbo].[Elements] WHERE [ElementName] = 'Plant')
BEGIN
    INSERT INTO [dbo].[Elements] ([ElementName], [Description])
    VALUES ('Plant', 'The element of nature and growth. Strong against Water, weak against Fire.');
    PRINT 'Element ''Plant'' inserted.';
END
ELSE
BEGIN
    PRINT 'Element ''Plant'' already exists.';
END
GO

-- =====================================================
-- SEED: Starter Monsters (5)
-- =====================================================
DECLARE @FireElementID INT = (SELECT [ElementID] FROM [dbo].[Elements] WHERE [ElementName] = 'Fire');
DECLARE @WaterElementID INT = (SELECT [ElementID] FROM [dbo].[Elements] WHERE [ElementName] = 'Water');
DECLARE @PlantElementID INT = (SELECT [ElementID] FROM [dbo].[Elements] WHERE [ElementName] = 'Plant');

-- Fire Slime
IF NOT EXISTS (SELECT * FROM [dbo].[MonsterCatalog] WHERE [MonsterName] = 'Fire Slime')
BEGIN
    INSERT INTO [dbo].[MonsterCatalog] ([MonsterName], [ElementID], [BaseHP], [BaseAttack], [BaseDefense], [BaseSpeed], [Description])
    VALUES ('Fire Slime', @FireElementID, 50, 15, 5, 10, 'A gelatinous creature infused with fire magic. Burns enemies on contact.');
    PRINT 'Monster ''Fire Slime'' inserted.';
END
ELSE
BEGIN
    PRINT 'Monster ''Fire Slime'' already exists.';
END
GO

-- Water Sprite
IF NOT EXISTS (SELECT * FROM [dbo].[MonsterCatalog] WHERE [MonsterName] = 'Water Sprite')
BEGIN
    DECLARE @WaterElementID2 INT = (SELECT [ElementID] FROM [dbo].[Elements] WHERE [ElementName] = 'Water');
    INSERT INTO [dbo].[MonsterCatalog] ([MonsterName], [ElementID], [BaseHP], [BaseAttack], [BaseDefense], [BaseSpeed], [Description])
    VALUES ('Water Sprite', @WaterElementID2, 45, 12, 8, 15, 'A swift water spirit that flows like a stream. Quick and evasive.');
    PRINT 'Monster ''Water Sprite'' inserted.';
END
ELSE
BEGIN
    PRINT 'Monster ''Water Sprite'' already exists.';
END
GO

-- Plant Guardian
IF NOT EXISTS (SELECT * FROM [dbo].[MonsterCatalog] WHERE [MonsterName] = 'Plant Guardian')
BEGIN
    DECLARE @PlantElementID2 INT = (SELECT [ElementID] FROM [dbo].[Elements] WHERE [ElementName] = 'Plant');
    INSERT INTO [dbo].[MonsterCatalog] ([MonsterName], [ElementID], [BaseHP], [BaseAttack], [BaseDefense], [BaseSpeed], [Description])
    VALUES ('Plant Guardian', @PlantElementID2, 80, 10, 20, 5, 'A sturdy plant creature with high defense. Slow but resilient.');
    PRINT 'Monster ''Plant Guardian'' inserted.';
END
ELSE
BEGIN
    PRINT 'Monster ''Plant Guardian'' already exists.';
END
GO

-- Fire Drake
IF NOT EXISTS (SELECT * FROM [dbo].[MonsterCatalog] WHERE [MonsterName] = 'Fire Drake')
BEGIN
    DECLARE @FireElementID2 INT = (SELECT [ElementID] FROM [dbo].[Elements] WHERE [ElementName] = 'Fire');
    INSERT INTO [dbo].[MonsterCatalog] ([MonsterName], [ElementID], [BaseHP], [BaseAttack], [BaseDefense], [BaseSpeed], [Description])
    VALUES ('Fire Drake', @FireElementID2, 100, 25, 12, 18, 'A fierce dragon-like creature that breathes fire. High attack power.');
    PRINT 'Monster ''Fire Drake'' inserted.';
END
ELSE
BEGIN
    PRINT 'Monster ''Fire Drake'' already exists.';
END
GO

-- Water Nymph
IF NOT EXISTS (SELECT * FROM [dbo].[MonsterCatalog] WHERE [MonsterName] = 'Water Nymph')
BEGIN
    DECLARE @WaterElementID3 INT = (SELECT [ElementID] FROM [dbo].[Elements] WHERE [ElementName] = 'Water');
    INSERT INTO [dbo].[MonsterCatalog] ([MonsterName], [ElementID], [BaseHP], [BaseAttack], [BaseDefense], [BaseSpeed], [Description])
    VALUES ('Water Nymph', @WaterElementID3, 60, 18, 10, 20, 'An elegant water spirit with balanced stats and high speed.');
    PRINT 'Monster ''Water Nymph'' inserted.';
END
ELSE
BEGIN
    PRINT 'Monster ''Water Nymph'' already exists.';
END
GO

-- =====================================================
-- SEED: Items (Potions and Swords)
-- =====================================================
DECLARE @FireElementID3 INT = (SELECT [ElementID] FROM [dbo].[Elements] WHERE [ElementName] = 'Fire');
DECLARE @WaterElementID4 INT = (SELECT [ElementID] FROM [dbo].[Elements] WHERE [ElementName] = 'Water');
DECLARE @PlantElementID3 INT = (SELECT [ElementID] FROM [dbo].[Elements] WHERE [ElementName] = 'Plant');

-- Health Potion
IF NOT EXISTS (SELECT * FROM [dbo].[Items] WHERE [ItemName] = 'Health Potion')
BEGIN
    INSERT INTO [dbo].[Items] ([ItemName], [ItemType], [ElementID], [StatBonus], [Description], [IsConsumable])
    VALUES ('Health Potion', 'Consumable', NULL, 50, 'Restores 50 HP when consumed.', 1);
    PRINT 'Item ''Health Potion'' inserted.';
END
ELSE
BEGIN
    PRINT 'Item ''Health Potion'' already exists.';
END
GO

-- Mana Potion
IF NOT EXISTS (SELECT * FROM [dbo].[Items] WHERE [ItemName] = 'Mana Potion')
BEGIN
    INSERT INTO [dbo].[Items] ([ItemName], [ItemType], [ElementID], [StatBonus], [Description], [IsConsumable])
    VALUES ('Mana Potion', 'Consumable', NULL, 30, 'Restores 30 MP when consumed.', 1);
    PRINT 'Item ''Mana Potion'' inserted.';
END
ELSE
BEGIN
    PRINT 'Item ''Mana Potion'' already exists.';
END
GO

-- Fire Sword
IF NOT EXISTS (SELECT * FROM [dbo].[Items] WHERE [ItemName] = 'Fire Sword')
BEGIN
    DECLARE @FireElementID4 INT = (SELECT [ElementID] FROM [dbo].[Elements] WHERE [ElementName] = 'Fire');
    INSERT INTO [dbo].[Items] ([ItemName], [ItemType], [ElementID], [StatBonus], [Description], [IsConsumable])
    VALUES ('Fire Sword', 'Weapon', @FireElementID4, 15, 'A sword imbued with fire magic. Increases attack by 15.', 0);
    PRINT 'Item ''Fire Sword'' inserted.';
END
ELSE
BEGIN
    PRINT 'Item ''Fire Sword'' already exists.';
END
GO

-- Water Sword
IF NOT EXISTS (SELECT * FROM [dbo].[Items] WHERE [ItemName] = 'Water Sword')
BEGIN
    DECLARE @WaterElementID5 INT = (SELECT [ElementID] FROM [dbo].[Elements] WHERE [ElementName] = 'Water');
    INSERT INTO [dbo].[Items] ([ItemName], [ItemType], [ElementID], [StatBonus], [Description], [IsConsumable])
    VALUES ('Water Sword', 'Weapon', @WaterElementID5, 15, 'A sword imbued with water magic. Increases attack by 15.', 0);
    PRINT 'Item ''Water Sword'' inserted.';
END
ELSE
BEGIN
    PRINT 'Item ''Water Sword'' already exists.';
END
GO

-- Plant Sword
IF NOT EXISTS (SELECT * FROM [dbo].[Items] WHERE [ItemName] = 'Plant Sword')
BEGIN
    DECLARE @PlantElementID4 INT = (SELECT [ElementID] FROM [dbo].[Elements] WHERE [ElementName] = 'Plant');
    INSERT INTO [dbo].[Items] ([ItemName], [ItemType], [ElementID], [StatBonus], [Description], [IsConsumable])
    VALUES ('Plant Sword', 'Weapon', @PlantElementID4, 15, 'A sword imbued with plant magic. Increases attack by 15.', 0);
    PRINT 'Item ''Plant Sword'' inserted.';
END
ELSE
BEGIN
    PRINT 'Item ''Plant Sword'' already exists.';
END
GO

-- =====================================================
-- VERIFICATION QUERIES
-- =====================================================
PRINT '';
PRINT '=====================================================';
PRINT 'Database Setup Complete!';
PRINT '=====================================================';
PRINT '';
PRINT 'Verification Summary:';
PRINT '';

-- Count Elements
DECLARE @ElementCount INT = (SELECT COUNT(*) FROM [dbo].[Elements]);
PRINT 'Elements: ' + CAST(@ElementCount AS VARCHAR(10));

-- Count Monsters
DECLARE @MonsterCount INT = (SELECT COUNT(*) FROM [dbo].[MonsterCatalog]);
PRINT 'Monsters: ' + CAST(@MonsterCount AS VARCHAR(10));

-- Count Items
DECLARE @ItemCount INT = (SELECT COUNT(*) FROM [dbo].[Items]);
PRINT 'Items: ' + CAST(@ItemCount AS VARCHAR(10));

PRINT '';
PRINT 'All tables created and seeded successfully!';
PRINT 'Database is ready for use.';
GO


