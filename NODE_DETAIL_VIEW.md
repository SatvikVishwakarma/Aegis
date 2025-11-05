# Node Detail View Feature

## Overview

The Node Detail View feature provides a hierarchical navigation system for viewing event and network logs. The Events page now displays nodes organized by groups, allowing administrators to browse by department, OS type, or environment, then drill down into individual node activity.

## Navigation Hierarchy

### Level 1: Events Page (Group View)
**Path**: `/dashboard/events`

Displays all nodes organized by their assigned groups:
- Shows group cards with node counts
- Lists all nodes within each group
- Provides statistics (total groups, total nodes)
- Real-time status indicators for each node

### Level 2: Node Detail Page (Logs View)
**Path**: `/dashboard/nodes/[id]`

Shows detailed logs for a specific node:
- Event logs tab (security events)
- Network logs tab (network connections)
- Node information and status

## Feature Access

### From Events Page
1. Go to **Dashboard > Events**
2. Browse the list of groups
3. Click on any **node** within a group
4. View that node's event and network logs

### From Nodes Page  
1. Go to **Dashboard > Nodes**
2. Click on any **node hostname** in the nodes table
3. View that node's event and network logs

## Events Page Sections

### 1. Page Header
- Title: "Event Viewer"
- Description: "Browse nodes by group to view their event and network logs"

### 2. Statistics Cards
Two stat cards showing:
- **Total Groups**: Count of all node groups (including "Ungrouped")
- **Total Nodes**: Total count of registered nodes

### 3. Group Cards

Each group is displayed in an expandable card showing:

#### Group Header
- Group icon with colored background
- Group name (e.g., "Production", "IT Department", "Linux Servers")
- Node count badge (e.g., "5 nodes")

#### Node List
For each node in the group:
- **Server Icon**: Visual indicator with hover effect
- **Hostname**: Node name in bold (clickable)
- **Status Indicator**: Green dot for online, gray for offline
- **Status Text**: "online" or "offline"
- **IP Address**: Displayed in monospace code format
- **Last Seen**: Relative timestamp (e.g., "2 minutes ago")
- **View Logs Button**: Blue badge with activity icon
- **Chevron Icon**: Right arrow indicating clickability

### 4. Ungrouped Nodes
Nodes without a group assignment appear in a special "Ungrouped" section at the bottom.

### 5. Empty State
When no nodes exist, displays:
- Large server icon
- "No Nodes Available" message
- Helpful instruction to register nodes

## Node Detail Page Sections

Displays key node details in a card layout:

- **Node ID**: Unique identifier (e.g., #1)
- **IP Address**: Node's IP address in monospace font
- **Status**: Visual indicator (online/offline) with pulsing animation for online nodes
- **Last Seen**: Relative timestamp (e.g., "2 minutes ago")
- **Group**: Node's assigned group (if any) with tag icon

### 2. Navigation
- Back button at top-left returns to nodes list
- Node hostname displayed as page title with server icon

### 3. Log Tabs

Two separate tabs organize logs by category:

#### Event Logs Tab
- Shows all non-network security events
- Event types include:
  - Failed Login
  - Successful Login
  - File Modified
  - Process Started
  - Privilege Escalation
  - Unauthorized Access
  - And any other non-network events

#### Network Logs Tab
- Shows network-related security events
- Event types include:
  - Network Connection
  - Any event type containing "network" or "connection"

### 4. Event Display

Each event card shows:
- **Icon**: Severity-based icon (critical, high, medium, low)
- **Event Type**: Human-readable event name
- **Severity Badge**: Color-coded severity level
- **Timestamp**: Full date and time
- **Details**: Expandable JSON payload with all event-specific data

#### Severity Levels and Colors
- **Critical**: Red (urgent security events)
- **High**: Orange (important security events)
- **Medium**: Yellow (warning-level events)
- **Low**: Blue (informational events)

## Technical Implementation

### Events Page (Group View)

**File**: `Dashboard/src/app/dashboard/events/page.tsx`

Key features:
- Fetches all nodes and groups them by the `group` field
- Creates Map structure: `Map<string, Node[]>`
- Nodes without groups go into "Ungrouped" category
- Alphabetical sorting with "Ungrouped" always last
- Real-time updates every 5 seconds via React Query
- Click handler navigates to `/dashboard/nodes/${node.id}`

#### Grouping Logic
```typescript
const groupedNodes = useMemo(() => {
  const groups = new Map<string, Node[]>()
  const ungrouped: Node[] = []
  
  nodes.forEach(node => {
    if (node.group) {
      if (!groups.has(node.group)) {
        groups.set(node.group, [])
      }
      groups.get(node.group)!.push(node)
    } else {
      ungrouped.push(node)
    }
  })
  
  if (ungrouped.length > 0) {
    groups.set('Ungrouped', ungrouped)
  }
  
  return groups
}, [nodes])
```

### Node Detail Page (Logs View)

**File**: `Dashboard/src/app/dashboard/nodes/[id]/page.tsx`

Key features:
- Next.js dynamic routing with `[id]` parameter
- React Query for data fetching with 5-second auto-refresh
- Tab state management for Event/Network log switching
- Filtering logic separates events based on event_type
- Framer Motion animations for smooth transitions

### API Integration

**Endpoint**: GET /api/v1/logs
**Parameters**:
- `node_id`: Filter events by specific node
- `limit`: Maximum events to retrieve (default: 1000)

**Function**: `fetchEvents({ node_id: nodeId, limit: 1000 })`

### Data Flow

1. Page loads with node ID from URL parameter
2. Fetches all nodes to get node details
3. Fetches events filtered by node_id
4. Separates events into two categories:
   - Network logs: event_type contains "network" or "connection"
   - Event logs: all other events
5. Displays appropriate logs based on selected tab
6. Auto-refreshes every 5 seconds

### Click Navigation

**Events Page**: `Dashboard/src/app/dashboard/events/page.tsx`
- Each node row is a clickable button element
- Hover effects: background color, icon color, text color changes
- Click navigates to `/dashboard/nodes/${node.id}`
- Visual feedback with "View Logs" badge and chevron icon

**Nodes Page**: `Dashboard/src/app/dashboard/nodes/page.tsx`
- Hostname cells are clickable buttons
- Hover shows external link icon
- Click navigates to `/dashboard/nodes/${node.id}`

## User Experience

### Loading States
- Skeleton loader displays while fetching events
- Smooth transitions between loading and loaded states
- No layout shift during load

### Empty States
- "No event logs found for this node" message when no events exist
- "No network logs found for this node" message when no network events exist
- Centered, styled empty state messages

### Real-time Updates
- Events automatically refresh every 5 seconds
- No page reload required
- New events animate in smoothly
- Tab counts update automatically

### Visual Design
- Consistent with overall Aegis dashboard theme
- Dark mode support
- Color-coded severity indicators
- Clean card-based layout
- Responsive design for different screen sizes

## Use Cases

### 1. Department-Based Monitoring
Organization by department:
1. Navigate to Events page
2. See groups like "IT Department", "HR", "Finance"
3. Click on nodes within specific department
4. Monitor department-specific security events

### 2. Environment-Based Monitoring
Separation by environment:
1. View groups like "Production", "Staging", "Development"
2. Quickly access production nodes for critical monitoring
3. Isolate staging environment issues
4. Review development environment activity

### 3. OS-Based Monitoring
Organization by operating system:
1. See groups like "Linux Servers", "Windows Servers", "macOS Workstations"
2. Monitor OS-specific security events
3. Compare behavior across different platforms
4. Platform-specific incident response

### 4. Security Investigation
When a security alert is triggered:
1. Navigate to the affected node's detail page
2. Review recent event logs for suspicious activity
3. Check network logs for unusual connections
4. Examine full event details in JSON format

### 2. Node Health Monitoring
Regular monitoring workflow:
1. Click on a node to view its activity
2. Verify last seen timestamp is recent
3. Check event logs for any errors or warnings
4. Review network connections for normal patterns

### 3. Incident Response
During a security incident:
1. Quickly access detailed logs for specific nodes
2. Filter by event type using the tab system
3. Export or analyze JSON event details
4. Correlate events across time

### 4. Compliance Auditing
For audit purposes:
1. Access historical logs for specific nodes
2. Review authentication events (logins)
3. Check file modification logs
4. Document network activity

## Benefits

### Organized Navigation
- Browse nodes by logical groupings (department, OS, environment)
- Quick visual overview of node distribution across groups
- Easy identification of group-specific nodes

### Improved Context
- See which group a node belongs to before viewing logs
- Understand node relationships and organizational structure
- Group-level statistics and insights

### Efficient Workflow
- Two-click navigation: Group view → Node view → Logs
- No need to remember node IDs or hostnames
- Visual indicators show node status at a glance

### Better Visibility
- Centralized view of all node activity
- Easy access to detailed event information
- Organized categorization of events

### Faster Investigation
- Direct navigation from node list
- No need to filter global event logs
- Separated network and event logs for targeted analysis

### Better Context
- Node information always visible
- Event details displayed with full context
- Severity indicators for quick assessment

### Enhanced Usability
- Intuitive tab-based interface
- Real-time updates without page refresh
- Responsive and accessible design

## Future Enhancements

Potential improvements for the node detail view:

1. **Time Range Filtering**
   - Add date range picker
   - Filter events by custom time periods
   - Quick filters (last hour, last 24 hours, last 7 days)

2. **Event Type Filtering**
   - Multi-select dropdown for event types
   - Quick filter buttons for common event types
   - Search within event details

3. **Export Functionality**
   - Export logs to CSV or JSON
   - Generate PDF reports
   - Copy filtered logs to clipboard

4. **Severity Filtering**
   - Filter by severity level
   - Toggle between severity levels
   - Highlight critical events

5. **Event Statistics**
   - Charts showing event distribution
   - Severity breakdown pie chart
   - Timeline graph of events

6. **Advanced Details**
   - Expandable/collapsible event details
   - Syntax highlighting for JSON
   - Copy individual fields

7. **Related Events**
   - Link related events together
   - Show event correlation
   - Timeline view of related activity

8. **Alert Configuration**
   - Set up alerts for specific events on this node
   - Configure notification thresholds
   - Email/SMS alerts for critical events

## Troubleshooting

### Node Not Found
If you see "Node not found":
- Verify the node ID in the URL is correct
- Check if the node still exists in the database
- Ensure you have permission to view the node

### No Logs Displayed
If no logs appear:
- Verify the node has generated events
- Check if agents are sending events properly
- Ensure the node_id in events matches the node
- Check browser console for API errors

### Slow Loading
If the page loads slowly:
- Check network connection to backend
- Verify backend server is running
- Consider reducing the limit parameter if too many events
- Check database performance

### Auto-refresh Not Working
If real-time updates stop:
- Check if React Query is properly configured
- Verify network connectivity
- Check browser console for errors
- Reload the page to restart updates

## API Reference

### Get Node Events
```
GET /api/v1/logs?node_id={node_id}&limit=1000
```

**Parameters**:
- `node_id` (required): Integer ID of the node
- `limit` (optional): Maximum number of events to return

**Response**:
```json
[
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
]
```

## Conclusion

The Node Detail View feature significantly enhances the Aegis monitoring system by providing focused, organized access to node-specific logs. The tabbed interface separates event and network logs for easier analysis, while the real-time updates ensure administrators always have current information. This feature is essential for effective security monitoring, incident response, and compliance auditing.
