namespace AegisAgent
{
    public class SecurityEvent
    {
        public string EventType { get; set; } = string.Empty;
        public string Severity { get; set; } = string.Empty;
        public Dictionary<string, object> Details { get; set; } = new();
        public DateTime Timestamp { get; set; } = DateTime.UtcNow;
    }

    public class NodeInfo
    {
        public int Id { get; set; }
        public string Hostname { get; set; } = string.Empty;
        public string IpAddress { get; set; } = string.Empty;
        public string? Group { get; set; }
        public string Status { get; set; } = string.Empty;
        public DateTime LastSeen { get; set; }
    }

    public class NodeRegistrationRequest
    {
        public string Hostname { get; set; } = string.Empty;
        public string IpAddress { get; set; } = string.Empty;
        public string? Group { get; set; }
    }

    public class HeartbeatRequest
    {
        public string Hostname { get; set; } = string.Empty;
    }

    public class EventIngestRequest
    {
        public int NodeId { get; set; }
        public string EventType { get; set; } = string.Empty;
        public string Severity { get; set; } = string.Empty;
        public Dictionary<string, object> Details { get; set; } = new();
    }
}
