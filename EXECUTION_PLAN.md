# Retro RPG Game Database - Execution Plan

## Overview
This document outlines the database architecture and execution plan for a Retro RPG game built with Python and SQL Server.

## Database Architecture

### Core Tables

#### 1. **Elements**
- Purpose: Defines elemental types (Fire, Water, Plant) for game mechanics
- Key Fields: ElementID (PK), ElementName, Description
- Relationships: Referenced by Items and MonsterCatalog

#### 2. **Players**
- Purpose: Stores player login credentials and account information
- Key Fields: PlayerID (PK), Username, PasswordHash, Email, CreatedDate
- Relationships: One-to-Many with SaveGames

#### 3. **MonsterCatalog**
- Purpose: Defines all available monsters with their base stats
- Key Fields: MonsterID (PK), MonsterName, ElementID (FK), BaseHP, BaseAttack, BaseDefense, BaseSpeed, Description
- Relationships: Many-to-One with Elements

#### 4. **Items**
- Purpose: Defines all items available in the game
- Key Fields: ItemID (PK), ItemName, ItemType, ElementID (FK, nullable), StatBonus, Description, IsConsumable
- Relationships: Many-to-One with Elements (optional)

#### 5. **SaveGames**
- Purpose: Stores player save game data including progress and position
- Key Fields: SaveGameID (PK), PlayerID (FK), Level, ExperiencePoints, CurrentHP, MaxHP, PositionX, PositionY, PositionZ, LastSaved
- Relationships: Many-to-One with Players, One-to-Many with Inventory

#### 6. **Inventory**
- Purpose: Links items to player save games (player's current inventory)
- Key Fields: InventoryID (PK), SaveGameID (FK), ItemID (FK), Quantity
- Relationships: Many-to-One with SaveGames, Many-to-One with Items

## Relationships Diagram

```
Players (1) ────< (Many) SaveGames
                         │
                         │ (1)
                         │
                         └───< (Many) Inventory
                                      │
                                      │ (Many)
                                      │
                                      └───> (1) Items
                                             │
                                             │ (Many)
                                             │
Elements (1) ────< (Many) Items
         │
         │ (Many)
         │
         └───< (Many) MonsterCatalog
```

## Execution Strategy

### Phase 1: Database Setup
1. Check if database exists, create if needed
2. Use database context

### Phase 2: Table Creation (Idempotent)
1. Create Elements table
2. Create Players table
3. Create MonsterCatalog table
4. Create Items table
5. Create SaveGames table
6. Create Inventory table

### Phase 3: Constraints & Relationships
1. Add Primary Keys
2. Add Foreign Keys
3. Add Check Constraints (where applicable)
4. Add Indexes for performance

### Phase 4: Data Seeding
1. Insert 3 Elements (Fire, Water, Plant)
2. Insert 5 Starter Monsters
3. Insert Basic Items (Potions, Sword variants)

### Phase 5: Verification
- Script includes error handling and validation

## Data Seeding Details

### Elements (3)
- Fire
- Water
- Plant

### Starter Monsters (5)
- Fire Slime (Fire element)
- Water Sprite (Water element)
- Plant Guardian (Plant element)
- Fire Drake (Fire element)
- Water Nymph (Water element)

### Items
- Health Potion (Consumable)
- Mana Potion (Consumable)
- Fire Sword (Weapon, Fire element)
- Water Sword (Weapon, Water element)
- Plant Sword (Weapon, Plant element)

## Best Practices Implemented
- ✅ Idempotency: All objects use IF NOT EXISTS checks
- ✅ Foreign Key constraints for data integrity
- ✅ Appropriate data types (INT, VARCHAR, DECIMAL, DATETIME2)
- ✅ Indexes on foreign keys for performance
- ✅ Default values where appropriate
- ✅ NOT NULL constraints for required fields


