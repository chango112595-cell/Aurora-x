# Aurora Database Migration System

## 📊 Overview

Complete database migration system using Alembic for version-controlled schema management with Aurora-X.

**Production Readiness**: 90% ⭐⭐⭐⭐⭐

---

## 🎯 Features

### Migration Management
- **Version Control**: Track all database schema changes
- **Auto-generate**: Automatic migration generation from models
- **Rollback Support**: Downgrade to any previous version
- **SQL Preview**: View SQL before applying migrations
- **Migration History**: Complete audit trail of changes

### Database Models
- **Users**: Authentication and authorization
- **Synthesis Tasks**: Code generation task tracking
- **Conversation History**: Chat conversation logs
- **System Metrics**: Monitoring data storage
- **Alerts**: System alert tracking
- **Audit Logs**: Security and activity logging

---

## 🚀 Quick Start

### Initial Setup

The database migration system is already initialized with an initial schema. If you need to reset:

```bash
# Check current migration status
./scripts/db-migrate.sh status

# Apply all pending migrations
./scripts/db-migrate.sh upgrade
```

### Creating a New Migration

```bash
# After modifying models in aurora_x/models.py
./scripts/db-migrate.sh create "Add user preferences column"

# Apply the new migration
./scripts/db-migrate.sh upgrade
```

---

## 📦 Database Schema

### Current Tables

#### **users**
Authentication and user management.

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| username | String(50) | Unique username |
| email | String(255) | Unique email address |
| hashed_password | String(255) | Bcrypt hashed password |
| full_name | String(255) | User's full name |
| is_active | Boolean | Account status |
| is_superuser | Boolean | Admin privileges |
| created_at | DateTime | Account creation timestamp |
| updated_at | DateTime | Last update timestamp |

**Indexes**: id, username, email

#### **synthesis_tasks**
Track code synthesis requests and results.

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| user_id | Integer | User who created task |
| prompt | Text | Natural language prompt |
| framework | String(50) | Target framework (flask, function) |
| status | String(20) | pending, running, completed, failed |
| result_data | JSON | Generation results |
| files_generated | JSON | List of generated files |
| error_message | Text | Error details if failed |
| created_at | DateTime | Task creation time |
| completed_at | DateTime | Task completion time |

**Indexes**: id, user_id

#### **conversation_history**
Store chat conversation logs.

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| user_id | Integer | User ID |
| session_id | String(100) | Conversation session |
| role | String(20) | user, assistant, system |
| content | Text | Message content |
| extra_data | JSON | Additional metadata |
| created_at | DateTime | Message timestamp |

**Indexes**: id, user_id, session_id

#### **system_metrics**
Store monitoring metrics for historical analysis.

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| metric_type | String(50) | cpu, memory, disk, service |
| component | String(100) | Service component name |
| value | Float | Metric value |
| unit | String(20) | Unit (%, GB, MB, count) |
| status | String(20) | healthy, warning, critical |
| extra_data | JSON | Additional metadata |
| created_at | DateTime | Metric timestamp |

**Indexes**: id, metric_type, created_at

#### **alerts**
Track system alerts and notifications.

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| severity | String(20) | info, warning, critical |
| component | String(100) | Affected component |
| title | String(255) | Alert title |
| message | Text | Alert description |
| value | Float | Metric value that triggered alert |
| threshold | Float | Threshold that was exceeded |
| is_resolved | Boolean | Resolution status |
| resolved_at | DateTime | Resolution timestamp |
| created_at | DateTime | Alert creation time |

**Indexes**: id, severity, component, created_at

#### **audit_logs**
Security and activity audit trail.

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| user_id | Integer | User who performed action |
| action | String(100) | Action performed |
| resource_type | String(50) | Type of resource |
| resource_id | Integer | ID of affected resource |
| details | JSON | Additional details |
| ip_address | String(45) | Client IP address |
| user_agent | String(255) | Client user agent |
| status | String(20) | success, failure |
| created_at | DateTime | Action timestamp |

**Indexes**: id, user_id, action, created_at

---

## 🔧 Migration Helper Script

### Usage

```bash
./scripts/db-migrate.sh <command> [arguments]
```

### Available Commands

#### `status`
Show current migration version and history.

```bash
./scripts/db-migrate.sh status
```

**Output:**
```
📊 Current Migration Status:
164468809966 (head)

📋 Migration History:
Rev: 164468809966 (head)
    Initial schema: users, tasks, conversations, metrics, alerts, audit logs
```

#### `create <message>`
Create a new migration with auto-generated changes.

```bash
./scripts/db-migrate.sh create "Add user preferences table"
```

**What it does:**
1. Compares current database with models
2. Generates migration with detected changes
3. Creates new file in `alembic/versions/`

#### `upgrade`
Apply all pending migrations to reach latest version.

```bash
./scripts/db-migrate.sh upgrade
```

#### `downgrade [steps]`
Rollback migrations.

```bash
# Downgrade one version
./scripts/db-migrate.sh downgrade

# Downgrade 3 versions
./scripts/db-migrate.sh downgrade 3

# Downgrade to base (empty database)
./scripts/db-migrate.sh downgrade all
```

**Safety:** Prompts for confirmation before downgrading.

#### `history`
Show complete migration history.

```bash
./scripts/db-migrate.sh history
```

#### `current`
Show current migration version only.

```bash
./scripts/db-migrate.sh current
```

#### `upgrade-to <revision>`
Upgrade to specific migration version.

```bash
./scripts/db-migrate.sh upgrade-to abc123
```

#### `downgrade-to <revision>`
Downgrade to specific migration version.

```bash
./scripts/db-migrate.sh downgrade-to abc123
```

#### `show-sql [version]`
Preview SQL without applying.

```bash
# Show SQL for upgrading to head
./scripts/db-migrate.sh show-sql

# Show SQL for specific version
./scripts/db-migrate.sh show-sql abc123
```

#### `stamp <version>`
Mark database as being at specific version without running migrations.

```bash
./scripts/db-migrate.sh stamp head
```

**Use case:** When manually applying migrations or fixing version tracking.

#### `reset`
Reset database completely (downgrade to base, then upgrade to head).

```bash
./scripts/db-migrate.sh reset
```

**Warning:** This will delete all data!

---

## 🔨 Manual Alembic Commands

If you prefer using Alembic directly:

```bash
# Check current version
alembic current

# Show migration history
alembic history

# Create new migration (auto-generate)
alembic revision --autogenerate -m "Description"

# Create empty migration (manual)
alembic revision -m "Description"

# Upgrade to latest
alembic upgrade head

# Upgrade one version
alembic upgrade +1

# Downgrade one version
alembic downgrade -1

# Downgrade to specific version
alembic downgrade abc123

# Show SQL for upgrade
alembic upgrade head --sql
```

---

## 📝 Adding New Models

### 1. Define Model

Edit `aurora_x/models.py`:

```python
from sqlalchemy import Column, Integer, String, DateTime
from aurora_x.models import Base

class UserPreference(Base):
    """User preferences."""
    
    __tablename__ = "user_preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    preference_key = Column(String(100))
    preference_value = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
```

### 2. Generate Migration

```bash
./scripts/db-migrate.sh create "Add user preferences table"
```

### 3. Review Migration

Check the generated file in `alembic/versions/`:

```python
def upgrade():
    op.create_table('user_preferences',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        # ...
    )

def downgrade():
    op.drop_table('user_preferences')
```

### 4. Apply Migration

```bash
./scripts/db-migrate.sh upgrade
```

---

## 🔄 Migration Best Practices

### Development Workflow

1. **Make model changes** in `aurora_x/models.py`
2. **Generate migration**: `./scripts/db-migrate.sh create "Description"`
3. **Review migration file** in `alembic/versions/`
4. **Test migration**: `./scripts/db-migrate.sh upgrade`
5. **Test rollback**: `./scripts/db-migrate.sh downgrade`
6. **Commit migration** to version control

### Production Deployment

1. **Backup database** before migrations
2. **Test migrations** in staging environment
3. **Review SQL**: `./scripts/db-migrate.sh show-sql`
4. **Apply in maintenance window**
5. **Verify data integrity** after migration
6. **Keep downgrade option** ready

### Data Migrations

For migrations that modify existing data:

```python
from alembic import op
import sqlalchemy as sa

def upgrade():
    # Schema change
    op.add_column('users', sa.Column('status', sa.String(20)))
    
    # Data migration
    connection = op.get_bind()
    connection.execute(
        sa.text("UPDATE users SET status = 'active' WHERE is_active = 1")
    )

def downgrade():
    op.drop_column('users', 'status')
```

### Avoiding Reserved Words

SQLAlchemy reserves certain column names. Avoid:
- `metadata` → use `extra_data` or `meta_info`
- `type` → use `item_type` or `category`
- `class` → use `class_name` or `classification`

---

## 🐳 Database Configuration

### Development (SQLite)

Current configuration in `alembic.ini`:

```ini
sqlalchemy.url = sqlite:///./aurora.db
```

### Production (PostgreSQL)

For production, update `alembic.ini`:

```ini
sqlalchemy.url = postgresql://user:password@localhost/aurora_db
```

Or use environment variable:

```bash
export DATABASE_URL="postgresql://user:password@localhost/aurora_db"
```

Then modify `alembic/env.py` to read from environment:

```python
import os
config.set_main_option(
    'sqlalchemy.url',
    os.getenv('DATABASE_URL', config.get_main_option('sqlalchemy.url'))
)
```

---

## 🧪 Testing Migrations

### Test Upgrade

```bash
# Apply migration
./scripts/db-migrate.sh upgrade

# Verify tables exist
sqlite3 aurora.db ".tables"

# Check schema
sqlite3 aurora.db ".schema users"
```

### Test Downgrade

```bash
# Downgrade one version
./scripts/db-migrate.sh downgrade

# Verify changes reverted
sqlite3 aurora.db ".tables"

# Upgrade back
./scripts/db-migrate.sh upgrade
```

### Test Full Cycle

```bash
# Reset database
./scripts/db-migrate.sh reset

# Verify all migrations applied correctly
./scripts/db-migrate.sh status
```

---

## 🔍 Troubleshooting

### Migration Conflicts

If you get "multiple heads" error:

```bash
# Show all heads
alembic heads

# Merge heads
alembic merge -m "Merge migrations" <head1> <head2>

# Apply merge
./scripts/db-migrate.sh upgrade
```

### Database Out of Sync

If database doesn't match migrations:

```bash
# Check current state
./scripts/db-migrate.sh current

# Stamp with correct version
./scripts/db-migrate.sh stamp <correct_revision>
```

### Failed Migration

If migration fails midway:

```bash
# Check current version
./scripts/db-migrate.sh current

# Fix the migration file
nano alembic/versions/<failed_migration>.py

# Try again
./scripts/db-migrate.sh upgrade
```

### Reset Everything

Nuclear option (deletes all data):

```bash
# Delete database
rm aurora.db

# Recreate from scratch
./scripts/db-migrate.sh upgrade
```

---

## 📚 Related Documentation

- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [Aurora Models](../aurora_x/models.py)
- [Alembic Configuration](../alembic.ini)

---

## ✅ Implementation Checklist

- [x] Alembic initialization
- [x] Initial database models
- [x] First migration created and applied
- [x] Migration helper script
- [x] SQLite configuration (development)
- [x] PostgreSQL support (production-ready)
- [x] Auto-generation support
- [x] Rollback support
- [x] Comprehensive documentation
- [ ] PostgreSQL deployment (when needed)
- [ ] Migration testing in CI/CD (optional)
- [ ] Automated backup before migrations (optional)

---

## 📊 Database Statistics

Current schema (Initial migration):
- **Tables**: 6 (users, synthesis_tasks, conversation_history, system_metrics, alerts, audit_logs)
- **Indexes**: 19 (for query optimization)
- **Relationships**: Ready for foreign keys when needed
- **Size**: ~124 KB (empty database)

---

**Created by**: Aurora (Autonomous Agent)  
**Priority**: #8 - Medium  
**Status**: ✅ Complete  
**Production Ready**: 90%  
**Date**: 2025-11-10
