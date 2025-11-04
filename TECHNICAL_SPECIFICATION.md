# AEGIS Security Monitoring System - Technical Specification

## Project Overview

Aegis is a comprehensive security monitoring and event management system built with a FastAPI backend and Next.js frontend. The system enables centralized monitoring of security nodes (agents), real-time event ingestion, policy management, and security event analysis through a web-based dashboard.

## Architecture

### Backend Stack
- Framework: FastAPI 0.121.0
- Python Version: 3.12+ (Linux) / 3.13.7 (Windows)
- Database: SQLite with async support (aiosqlite)
- ORM: SQLAlchemy 2.0.44 with async extensions
- Authentication: JWT (python-jose) with bcrypt password hashing
- WebSocket: Real-time updates via FastAPI WebSocket support
- ASGI Server: Uvicorn 0.38.0 with reload support

### Frontend Stack
- Framework: Next.js 14.2.33
- Language: TypeScript
- State Management: TanStack Query (React Query)
- Styling: Tailwind CSS
- Animation: Framer Motion
- HTTP Client: Axios with interceptors
- Search: Fuse.js for fuzzy search
- Notifications: React Hot Toast

## Database Schema

### Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255),
    hashed_password VARCHAR(255) NOT NULL,
    disabled BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### Nodes Table
```sql
CREATE TABLE nodes (
    id INTEGER PRIMARY KEY,
    hostname VARCHAR(255) UNIQUE NOT NULL,
    ip_address VARCHAR(45) UNIQUE NOT NULL,
    "group" VARCHAR(100),
    last_seen DATETIME DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) DEFAULT 'offline' NOT NULL
);

CREATE INDEX ix_nodes_hostname ON nodes (hostname);
CREATE INDEX ix_nodes_group ON nodes ("group");
```

### Events Table
```sql
CREATE TABLE events (
    id INTEGER PRIMARY KEY,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    event_type VARCHAR(100) NOT NULL,
    severity VARCHAR(50) NOT NULL,
    details JSON,
    node_id INTEGER NOT NULL,
    FOREIGN KEY (node_id) REFERENCES nodes (id)
);

CREATE INDEX ix_events_timestamp ON events (timestamp);
CREATE INDEX ix_events_event_type ON events (event_type);
CREATE INDEX ix_events_severity ON events (severity);
```

### Policies Table
```sql
CREATE TABLE policies (
    id INTEGER PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    type VARCHAR(100) NOT NULL,
    rules_json JSON NOT NULL
);
```

### Node-Policy Association Table
```sql
CREATE TABLE node_policy_association (
    node_id INTEGER NOT NULL,
    policy_id INTEGER NOT NULL,
    PRIMARY KEY (node_id, policy_id),
    FOREIGN KEY (node_id) REFERENCES nodes (id),
    FOREIGN KEY (policy_id) REFERENCES policies (id)
);
```

## API Endpoints

### Authentication Endpoints
- POST /api/v1/auth/login - User authentication, returns JWT token
- GET /api/v1/auth/verify - Verify JWT token validity

### Node Management Endpoints
- GET /api/v1/nodes - List all nodes
- POST /api/v1/nodes/register - Register new node or update existing
- POST /api/v1/nodes/heartbeat - Node heartbeat check-in
- PUT /api/v1/nodes/{node_id} - Update node details (hostname, ip_address, group)
- DELETE /api/v1/nodes/{node_id} - Delete node (requires admin password)

### Event/Log Endpoints
- POST /api/v1/logs/ingest - Ingest security event from agent
- GET /api/v1/logs - Query events with filters (node_id, severity, event_type, start_time, end_time, limit)

### Policy Endpoints
- GET /api/v1/policies - List all policies
- POST /api/v1/policies - Create new policy
- DELETE /api/v1/policies/{policy_id} - Delete policy (requires admin password)
- POST /api/v1/policies/assign - Assign policy to node

## Authentication & Security

### JWT Authentication
- Algorithm: HS256
- Token Expiration: 30 minutes (configurable)
- Token Storage: localStorage in frontend
- Header Format: Authorization: Bearer {token}

### Password Security
- Hashing: bcrypt with automatic salt generation
- Admin Password: Auto-generated 10-character password on first setup
- Password Confirmation: Required for destructive operations (delete node, delete policy)

### API Key Authentication
- AGENT_API_KEY: Used by agents for event ingestion
- DASHBOARD_API_KEY: Optional additional security layer for dashboard
- Header: X-Dashboard-Key (optional)

### Environment Variables
```
SECRET_KEY=base64-encoded-32-bytes
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
AGENT_API_KEY=base64-encoded-32-bytes
DASHBOARD_API_KEY=base64-encoded-32-bytes
DATABASE_URL=sqlite+aiosqlite:///./aegis.db
```

## Event Ingestion System

### Event Schema
```json
{
  "node_id": 1,
  "event_type": "failed_login",
  "severity": "high",
  "details": {
    "username": "root",
    "source_ip": "192.168.1.100",
    "timestamp": "2025-11-04T10:30:00Z",
    "additional_info": {}
  }
}
```

### Severity Levels
- low: Informational events
- medium: Warning events
- high: Critical security events requiring attention
- critical: Immediate action required

### Event Types (Examples)
- failed_login
- successful_login
- file_modified
- process_started
- network_connection
- privilege_escalation
- unauthorized_access

### Event Processing Flow
1. Agent sends POST request to /api/v1/logs/ingest
2. Validate AGENT_API_KEY
3. Validate node_id exists
4. Convert event to dictionary for rule evaluation
5. Evaluate against detection rules
6. Store event in database
7. Broadcast event via WebSocket to connected dashboards
8. Return created event and triggered rule names

## WebSocket System

### WebSocket Endpoint
- URL: ws://localhost:8000/ws
- Protocol: JSON message-based

### Message Types
```json
{
  "type": "node_created",
  "data": {NodeResponse}
}

{
  "type": "node_updated",
  "data": {NodeResponse}
}

{
  "type": "node_deleted",
  "data": {"id": 1}
}

{
  "type": "event_created",
  "data": {EventResponse},
  "triggered_rules": ["rule_name_1"]
}
```

### Connection Management
- Automatic reconnection on disconnect
- Broadcast to all connected clients
- Connection state tracking per client

## Node Grouping System

### Group Functionality
- Optional VARCHAR(100) field on nodes table
- Indexed for performance
- Use cases: Department (IT, HR), OS type (Linux, Windows), Environment (Production, Staging)
- Filter nodes by group in dashboard
- Include group in search queries

### Group Assignment
- Via POST /api/v1/nodes/register with "group" field
- Via PUT /api/v1/nodes/{node_id} to update group
- Null/empty values allowed

## Node Detail View

### Individual Node Monitoring
The dashboard provides a dedicated detail page for each node to view all associated logs and activity.

### Navigation
- Click on any node hostname in the nodes table
- Opens new page at /dashboard/nodes/[id]
- Back button returns to nodes list

### Node Information Display
- Node ID
- IP Address
- Current status (online/offline)
- Last seen timestamp
- Group assignment (if applicable)

### Log Categories
The node detail page organizes logs into two tabs:

1. Event Logs Tab
   - Displays all non-network events for the node
   - Includes: failed_login, successful_login, file_modified, process_started, privilege_escalation, unauthorized_access
   - Shows severity level with color-coded badges
   - Displays full event details in JSON format
   - Auto-refreshes every 5 seconds

2. Network Logs Tab
   - Displays network-related events only
   - Includes: network_connection and any event_type containing "network" or "connection"
   - Shows connection details: source IP, destination IP, port, protocol
   - Same formatting and refresh rate as event logs

### Event Display Format
Each event shows:
- Event type (formatted as readable text)
- Severity badge (critical, high, medium, low)
- Timestamp (full date and time)
- Detailed JSON payload with all event-specific information

### Real-time Updates
- Fetches events for specific node_id using GET /api/v1/logs?node_id={id}&limit=1000
- Automatic refresh every 5 seconds via React Query
- Shows loading skeleton during initial fetch
- Smooth animations for new events

## Detection Rules System

### Rule Engine Location
Server/rules.py

### Rule Evaluation Function
```python
def evaluate_event(event_dict: dict) -> List[str]:
    """
    Evaluates an event against all detection rules.
    Returns list of triggered rule names.
    """
```

### Rule Structure (Example)
```python
{
    "name": "Multiple Failed Logins",
    "condition": lambda event: (
        event.get("event_type") == "failed_login" and
        event.get("severity") in ["high", "critical"]
    ),
    "action": "alert"
}
```

## File Structure

### Backend (Server/)
```
Server/
├── app.py                  # FastAPI application entry point
├── authentication.py       # JWT auth, password hashing, user management
├── auth_routes.py          # Authentication endpoints
├── database_setup.py       # Database initialization script
├── db.py                   # Database connection and session management
├── models.py               # SQLAlchemy ORM models
├── schemas.py              # Pydantic request/response schemas
├── nodes.py                # Node management endpoints
├── policies.py             # Policy management endpoints
├── logs.py                 # Event ingestion and query endpoints
├── rules.py                # Detection rules engine
├── websocket.py            # WebSocket connection manager
├── migrate_add_group.py    # Database migration script
├── requirments.txt         # Python dependencies
├── .env                    # Environment variables (generated)
├── aegis.db                # SQLite database (generated)
└── aegis/                  # Python virtual environment
```

### Frontend (Dashboard/)
```
Dashboard/
├── src/
│   ├── app/
│   │   ├── layout.tsx              # Root layout with providers
│   │   ├── page.tsx                # Landing page
│   │   ├── globals.css             # Global styles
│   │   ├── login/
│   │   │   └── page.tsx            # Login page
│   │   └── dashboard/
│   │       ├── layout.tsx          # Dashboard layout with navigation
│   │       ├── page.tsx            # Dashboard overview
│   │       ├── nodes/
│   │       │   ├── page.tsx        # Node management page
│   │       │   └── [id]/
│   │       │       └── page.tsx    # Individual node detail page (event/network logs)
│   │       ├── events/
│   │       │   └── page.tsx        # Event logs page
│   │       └── policies/
│   │           └── page.tsx        # Policy management page
│   ├── components/
│   │   ├── providers/
│   │   │   ├── QueryProvider.tsx   # React Query provider
│   │   │   └── ThemeProvider.tsx   # Dark/light theme provider
│   │   └── ui/
│   │       ├── CommandPalette.tsx  # Keyboard shortcuts
│   │       ├── Modal.tsx           # Modal component
│   │       ├── Skeleton.tsx        # Loading skeletons
│   │       └── StatCard.tsx        # Dashboard statistics cards
│   ├── lib/
│   │   ├── api.ts                  # API client with axios
│   │   └── utils.ts                # Utility functions
│   ├── store/
│   │   └── index.ts                # State management
│   └── types/
│       └── index.ts                # TypeScript type definitions
├── package.json
├── tsconfig.json
├── tailwind.config.ts
├── next.config.js
└── .env.local                       # Frontend environment variables
```

## Server Setup and Deployment

### Windows Setup
Execute: setup_and_start.ps1
Steps:
1. Generate secure random keys for SECRET_KEY, AGENT_API_KEY, DASHBOARD_API_KEY
2. Create .env file with generated keys
3. Create Python virtual environment (aegis/)
4. Activate virtual environment
5. Install dependencies from requirments.txt
6. Initialize database with database_setup.py
7. Create admin user with auto-generated password
8. Start uvicorn server on 0.0.0.0:8000 with reload

### Linux Setup
Execute: setup_and_start.sh
Similar steps to Windows with bash syntax

### Server Binding
- Host: 0.0.0.0 (accessible from network)
- Port: 8000
- Reload: Enabled for development
- Production: Disable reload, use process manager (systemd)

## Dashboard Setup and Deployment

### Setup Script
Execute: setup_and_start.ps1 (Windows) or setup_and_start.sh (Linux)
Steps:
1. Check Node.js and npm installation
2. Create .env.local with API endpoints
3. Install npm dependencies
4. Start Next.js development server on localhost:3000
5. Auto-open browser

### Environment Variables
```
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws
NEXT_PUBLIC_DASHBOARD_API_KEY=optional-api-key
```

## Agent Requirements and Specifications

### Agent Core Functionality
Agents must implement the following capabilities:

1. Node Registration
   - Endpoint: POST /api/v1/nodes/register
   - Required fields: hostname, ip_address
   - Optional fields: group
   - Include AGENT_API_KEY in X-API-Key header

2. Heartbeat Mechanism
   - Endpoint: POST /api/v1/nodes/heartbeat
   - Frequency: Every 60 seconds recommended
   - Payload: {"hostname": "agent-hostname"}
   - Updates node status to "online"

3. Event Collection and Ingestion
   - Endpoint: POST /api/v1/logs/ingest
   - Required fields: node_id, event_type, severity, details
   - Include AGENT_API_KEY in X-API-Key header
   - JSON payload format

### Event Data Collection Points

#### System Logs
- Monitor /var/log/auth.log (Linux) or Security Event Log (Windows)
- Parse login attempts (successful and failed)
- Extract username, source IP, timestamp
- Categorize by severity based on patterns

#### File System Monitoring
- Watch critical directories (/etc, /var/www, application directories)
- Detect file creation, modification, deletion
- Capture file path, operation type, user, timestamp
- Hash file changes for integrity verification

#### Process Monitoring
- Track process creation and termination
- Monitor for suspicious process names or paths
- Capture process ID, parent process, command line arguments
- Detect privilege escalation attempts

#### Network Monitoring
- Monitor network connections (incoming and outgoing)
- Capture source IP, destination IP, port, protocol
- Detect unusual connection patterns
- Track listening services

#### User Activity
- Monitor user logins and logouts
- Track sudo/privilege escalation usage
- Capture command history for privileged users
- Detect after-hours access

### Agent Implementation Requirements

#### Technology Stack
- Language: Python 3.8+ (recommended) or any language with HTTP client support
- Dependencies: requests/httpx for API calls, watchdog for file monitoring, psutil for process monitoring
- Configuration: JSON or YAML configuration file
- Logging: Local logging with rotation for troubleshooting

#### Configuration File Schema
```json
{
  "server": {
    "api_url": "http://localhost:8000/api/v1",
    "api_key": "base64-encoded-agent-key",
    "verify_ssl": true
  },
  "node": {
    "hostname": "auto-detect-or-override",
    "ip_address": "auto-detect-or-override",
    "group": "Production"
  },
  "monitoring": {
    "heartbeat_interval": 60,
    "event_batch_size": 10,
    "event_batch_interval": 5
  },
  "collectors": {
    "system_logs": {
      "enabled": true,
      "paths": ["/var/log/auth.log", "/var/log/syslog"]
    },
    "file_monitor": {
      "enabled": true,
      "watch_paths": ["/etc", "/var/www"],
      "exclude_patterns": ["*.tmp", "*.swp"]
    },
    "process_monitor": {
      "enabled": true,
      "scan_interval": 10
    },
    "network_monitor": {
      "enabled": true,
      "scan_interval": 30
    }
  }
}
```

#### Agent Workflow
1. Load configuration from file
2. Register with server (POST /api/v1/nodes/register)
3. Start heartbeat thread (POST /api/v1/nodes/heartbeat every 60s)
4. Initialize event collectors based on configuration
5. Start collector threads for each enabled monitor
6. Queue events in memory buffer
7. Batch send events to server (POST /api/v1/logs/ingest)
8. Handle API errors with exponential backoff retry
9. Log agent activity locally
10. Graceful shutdown on SIGTERM

#### Error Handling
- Network failures: Queue events locally, retry with exponential backoff
- Authentication failures: Log error, alert administrator
- Server unavailable: Continue collecting, store events up to buffer limit
- Invalid configuration: Fail fast with clear error message

#### Security Considerations
- Store API key securely (file permissions 600)
- Use HTTPS for production deployments
- Validate SSL certificates
- Rotate API keys periodically
- Run agent with minimal required privileges
- Sanitize sensitive data before sending events

### Event Mapping Examples

#### Failed SSH Login
```json
{
  "node_id": 1,
  "event_type": "failed_login",
  "severity": "medium",
  "details": {
    "protocol": "ssh",
    "username": "admin",
    "source_ip": "192.168.1.50",
    "timestamp": "2025-11-04T10:15:30Z",
    "reason": "invalid_password"
  }
}
```

#### Suspicious File Modification
```json
{
  "node_id": 1,
  "event_type": "file_modified",
  "severity": "high",
  "details": {
    "file_path": "/etc/passwd",
    "operation": "write",
    "user": "www-data",
    "timestamp": "2025-11-04T10:20:45Z",
    "file_hash_before": "abc123...",
    "file_hash_after": "def456..."
  }
}
```

#### Privilege Escalation
```json
{
  "node_id": 1,
  "event_type": "privilege_escalation",
  "severity": "critical",
  "details": {
    "user": "webuser",
    "command": "sudo su -",
    "timestamp": "2025-11-04T10:25:00Z",
    "success": true
  }
}
```

#### Unusual Network Connection
```json
{
  "node_id": 1,
  "event_type": "network_connection",
  "severity": "high",
  "details": {
    "direction": "outbound",
    "source_ip": "192.168.1.10",
    "destination_ip": "suspicious.domain.com",
    "destination_port": 4444,
    "protocol": "tcp",
    "timestamp": "2025-11-04T10:30:15Z"
  }
}
```

## API Response Formats

### Node Response
```json
{
  "id": 1,
  "hostname": "web-server-01",
  "ip_address": "192.168.1.10",
  "group": "Production",
  "status": "online",
  "last_seen": "2025-11-04T10:30:00"
}
```

### Event Response
```json
{
  "id": 1,
  "node_id": 1,
  "timestamp": "2025-11-04T10:30:00",
  "event_type": "failed_login",
  "severity": "high",
  "details": {
    "username": "admin",
    "source_ip": "192.168.1.50"
  }
}
```

### Event Ingest Response
```json
{
  "created_event": {EventResponse},
  "triggered_rules": ["Multiple Failed Logins", "Brute Force Detection"]
}
```

## Database Initialization

### Admin User Creation
- Username: admin (fixed)
- Email: admin@aegis.local
- Password: Auto-generated 10-character alphanumeric
- Displayed once during database_setup.py execution
- Required for dashboard login and delete confirmations

### Database Migration
- Script: migrate_add_group.py
- Purpose: Add group column to existing databases
- Safe to run multiple times (checks if column exists)
- Creates index on group column automatically

## Production Deployment Considerations

### Backend
- Use production ASGI server (Gunicorn with Uvicorn workers)
- Disable debug mode and reload
- Use PostgreSQL instead of SQLite for better concurrency
- Implement rate limiting
- Set up HTTPS with valid SSL certificates
- Configure firewall rules (allow port 8000)
- Use environment-specific .env files
- Implement log rotation
- Set up monitoring and alerting

### Frontend
- Build production bundle: npm run build
- Serve with production server (nginx, Apache)
- Configure reverse proxy
- Enable HTTPS
- Set up CDN for static assets
- Configure CORS properly
- Implement security headers

### Security Hardening
- Change default admin password immediately
- Rotate API keys regularly
- Use strong SECRET_KEY (32+ bytes)
- Implement IP whitelisting for sensitive endpoints
- Enable audit logging
- Regular security updates
- Database backups and disaster recovery
- Principle of least privilege for all components

## Testing Endpoints

### Health Check
GET /health
Returns: {"status": "ok"}

### API Documentation
GET /docs
Returns: Interactive Swagger UI

GET /redoc
Returns: ReDoc documentation

## Dependencies

### Backend Python Packages
- fastapi==0.121.0
- uvicorn[standard]==0.38.0
- sqlalchemy[asyncio]==2.0.44
- aiosqlite==0.21.0
- pydantic==2.12.3
- bcrypt==5.0.0
- python-jose[cryptography]==3.5.0
- python-dotenv==1.2.1
- python-multipart==0.0.20
- requests==2.32.5
- httpx==0.28.1
- loguru==0.7.3

### Frontend Node Packages
- next==14.2.33
- react==18.3.1
- typescript==5.7.3
- tailwindcss==3.4.1
- @tanstack/react-query==5.64.0
- axios==1.7.9
- framer-motion==11.15.0
- fuse.js==7.0.0
- react-hot-toast==2.4.1
- lucide-react==0.469.0

## Performance Considerations

### Database Optimization
- Indexed columns: hostname, ip_address, group, timestamp, event_type, severity
- Async database operations throughout
- Connection pooling via SQLAlchemy
- Query optimization with proper WHERE clauses

### Caching Strategy
- React Query for frontend data caching
- 5-second refetch interval for real-time data
- Optimistic updates for better UX

### WebSocket Optimization
- Broadcast only to active connections
- JSON serialization for all messages
- Automatic cleanup of disconnected clients

## Logging and Monitoring

### Server Logs
- Location: stdout/stderr (captured by Uvicorn)
- Format: JSON structured logs (via Loguru)
- Levels: DEBUG, INFO, WARNING, ERROR, CRITICAL

### Event Logs
- Stored in events table
- Queryable via /api/v1/logs endpoint
- Filterable by node, severity, type, time range

### Audit Trail
- User authentication events
- Node registration/deletion
- Policy creation/deletion
- All administrative actions

## Agent Development Guidelines

### Minimum Viable Agent
1. Register node on startup
2. Send heartbeat every 60 seconds
3. Monitor system logs for authentication events
4. Send events to server in real-time
5. Handle network errors gracefully

### Recommended Agent Features
1. Configurable monitoring modules
2. Event batching for efficiency
3. Local event queue with persistence
4. Automatic retry with exponential backoff
5. Health check endpoint
6. Metrics collection (events/second, errors, queue size)
7. Graceful shutdown handling
8. Log rotation
9. Self-update mechanism
10. Platform detection and auto-configuration

### Agent Testing
1. Unit tests for each collector
2. Integration tests with mock server
3. Load testing with high event volume
4. Network failure simulation
5. Resource usage monitoring (CPU, memory, disk)
6. Long-running stability tests

## System Limits and Constraints

### Database
- SQLite: Single writer limitation (use PostgreSQL for high concurrency)
- Event retention: No automatic cleanup (implement archival strategy)
- Maximum event details size: JSON text field limit

### API Rate Limits
- Not currently implemented (add in production)
- Recommended: 100 requests/minute per node
- Recommended: 1000 events/minute per node

### WebSocket
- Maximum concurrent connections: Unlimited (limited by server resources)
- Message size: No hard limit (practical limit ~1MB)

### Frontend
- Browser localStorage for JWT token
- Session timeout: 30 minutes (configurable)
- Maximum table rows displayed: 100 (pagination recommended)

## Future Enhancements

### Planned Features
- Multi-user support with role-based access control
- Advanced detection rules with machine learning
- Event correlation and pattern detection
- Automated response actions (block IP, isolate node)
- Email/SMS alerting
- PDF report generation
- Dashboard customization
- Multi-tenant support
- API versioning
- GraphQL endpoint option
- Elasticsearch integration for log storage
- Grafana integration for metrics
- Incident response workflow
- Compliance reporting (PCI-DSS, HIPAA, SOC2)

### Scalability Improvements
- Horizontal scaling with load balancer
- Redis for session management
- Message queue for event processing (RabbitMQ, Kafka)
- Time-series database for metrics (InfluxDB)
- Distributed tracing (Jaeger, Zipkin)
- Container orchestration (Kubernetes)
- Microservices architecture for components

## Support and Documentation

### Additional Documentation Files
- README.md: Project overview and quick start
- AUTHENTICATION_COMPLETE.md: Authentication system details
- FRESH_START.md: Clean installation guide
- GROUP_FEATURE.md: Node grouping functionality
- TECHNICAL_SPECIFICATION.md: This document

### Setup Scripts
- Server/setup_and_start.ps1: Windows server setup
- Server/setup_and_start.sh: Linux server setup
- Dashboard/setup_and_start.ps1: Windows dashboard setup
- Dashboard/setup_and_start.sh: Linux dashboard setup

### Database Scripts
- Server/database_setup.py: Initialize database and create admin user
- Server/migrate_add_group.py: Add group column to existing database

## Contact and Contribution

This specification provides all necessary technical details for implementing security monitoring agents that integrate with the Aegis platform. Agents must implement node registration, heartbeat mechanism, and event ingestion as specified to ensure proper integration with the centralized monitoring system.