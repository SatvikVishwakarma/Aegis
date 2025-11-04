# Node Groups Feature

## Overview
The Node Groups feature allows you to organize and categorize your security nodes by department, OS type, environment, or any custom classification that fits your organization's needs.

## Features

### Backend (Server)
- **New `group` column** in the `nodes` table (VARCHAR(100), indexed)
- **API support** for creating, updating, and filtering nodes by group
- **Optional field** - groups can be null/empty
- **WebSocket updates** - group changes broadcast in real-time

### Frontend (Dashboard)
- **Group filter dropdown** - Filter nodes by group
- **Group badges** - Visual tags showing each node's group
- **Add/Edit support** - Assign groups when creating or editing nodes
- **Search integration** - Search includes group names

## Usage

### Assigning Groups

#### Via Dashboard UI
1. Click **"Add Node"** or **Edit** an existing node
2. Enter the group name in the **"Group (Optional)"** field
3. Examples: `IT`, `HR`, `Linux`, `Windows`, `Production`, `Development`
4. Click **Save**

#### Via API
```bash
# Register a new node with a group
POST /api/v1/nodes/register
{
  "hostname": "web-server-01",
  "ip_address": "192.168.1.100",
  "group": "Production"
}

# Update an existing node's group
PUT /api/v1/nodes/{node_id}
{
  "group": "Linux"
}
```

### Filtering Nodes

#### Via Dashboard
- Use the **"Filter by Group"** dropdown in the Nodes page
- Select a group to see only nodes in that category
- Select **"All Groups"** to see all nodes

#### Via Search
- The search bar includes group names
- Type a group name to find all nodes in that group
- Combines with hostname and IP search

## Group Examples

### By Department
- `IT`
- `HR`
- `Finance`
- `Engineering`
- `Marketing`

### By Operating System
- `Linux`
- `Windows`
- `macOS`
- `Ubuntu`
- `CentOS`

### By Environment
- `Production`
- `Development`
- `Staging`
- `Testing`
- `QA`

### By Location
- `Office-NY`
- `Office-LA`
- `Datacenter-1`
- `Cloud-AWS`
- `Cloud-Azure`

### By Function
- `Web-Servers`
- `Database-Servers`
- `API-Servers`
- `Mail-Servers`
- `DNS-Servers`

## Database Schema

```sql
-- Nodes table with group column
CREATE TABLE nodes (
    id INTEGER PRIMARY KEY,
    hostname VARCHAR(255) NOT NULL UNIQUE,
    ip_address VARCHAR(45) NOT NULL UNIQUE,
    "group" VARCHAR(100),  -- New column
    last_seen DATETIME,
    status VARCHAR(50) DEFAULT 'offline'
);

-- Index for faster group-based queries
CREATE INDEX ix_nodes_group ON nodes ("group");
```

## Migration

If you have an existing database, run the migration script:

```powershell
# Windows
cd Server
python migrate_add_group.py

# Linux/Mac
cd Server
python3 migrate_add_group.py
```

The migration script will:
1. Check if the `group` column exists
2. Add it if missing
3. Create an index for performance
4. Report success/failure

## API Endpoints

### List Nodes (with groups)
```http
GET /api/v1/nodes
```

**Response:**
```json
[
  {
    "id": 1,
    "hostname": "web-server-01",
    "ip_address": "192.168.1.100",
    "group": "Production",
    "status": "online",
    "last_seen": "2025-11-04T10:30:00"
  }
]
```

### Register Node (with group)
```http
POST /api/v1/nodes/register
Content-Type: application/json

{
  "hostname": "db-server-02",
  "ip_address": "192.168.1.101",
  "group": "Linux"
}
```

### Update Node Group
```http
PUT /api/v1/nodes/{node_id}
Content-Type: application/json

{
  "group": "Production"
}
```

## Best Practices

1. **Consistent Naming**
   - Use consistent capitalization (e.g., always "Production" not "production")
   - Avoid special characters
   - Keep names short and descriptive

2. **Hierarchical Groups**
   - Use hyphens for sub-categories: `Prod-Web`, `Prod-DB`
   - Or use slashes: `Production/Web`, `Production/Database`

3. **Group Size**
   - Aim for 5-20 nodes per group for manageability
   - Too many groups = harder to filter
   - Too few groups = less useful organization

4. **Documentation**
   - Document your group naming convention
   - Share with your team
   - Update as your infrastructure grows

## Troubleshooting

### Group not showing in dropdown?
- The dropdown only shows groups that are actually assigned to nodes
- Create a node with that group first

### Can't filter by group?
- Make sure you've selected a group from the dropdown
- Check that nodes actually have that group assigned

### Migration failed?
- Check database file exists: `Server/aegis.db`
- Ensure no other process is using the database
- Check file permissions

## Future Enhancements

Potential future features for groups:
- [ ] Group-based policy assignment
- [ ] Group-level permissions
- [ ] Multi-group support (tags)
- [ ] Group hierarchies/nesting
- [ ] Color-coded group badges
- [ ] Group statistics dashboard
- [ ] Bulk group assignment
- [ ] Import/export group configurations
