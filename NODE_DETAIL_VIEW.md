# Node Detail View Feature

## Overview

The Node Detail View feature provides a dedicated page for viewing all event and network logs associated with a specific node. This allows administrators to drill down into individual node activity and investigate security events more effectively.

## Feature Access

### Navigation
1. Go to Dashboard > Nodes
2. Click on any node's hostname in the nodes table
3. The node detail page opens showing comprehensive node information and logs

### URL Pattern
```
/dashboard/nodes/[id]
```
Where `[id]` is the numeric node ID.

## Page Sections

### 1. Node Information Header

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

### Frontend Components

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

**File**: `Dashboard/src/app/dashboard/nodes/page.tsx`

Updated hostname cell to be clickable:
```tsx
<button
  onClick={() => router.push(`/dashboard/nodes/${node.id}`)}
  className="flex items-center gap-2 group hover:bg-slate-100"
>
  <Server className="w-4 h-4 text-slate-400" />
  <span className="font-medium group-hover:text-primary">
    {node.hostname}
  </span>
  <ExternalLink className="w-3 h-3 opacity-0 group-hover:opacity-100" />
</button>
```

Visual feedback:
- Hover effect with background color change
- Text color changes to primary blue
- ExternalLink icon appears on hover
- Cursor changes to pointer

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

### 1. Security Investigation
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

### Improved Visibility
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
