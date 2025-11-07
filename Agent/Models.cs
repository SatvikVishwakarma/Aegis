using Newtonsoft.Json;

namespace AegisAgent
{
    public class SecurityEvent
    {
        [JsonProperty("event_type")]
        public string EventType { get; set; } = string.Empty;
        
        [JsonProperty("severity")]
        public string Severity { get; set; } = string.Empty;
        
        [JsonProperty("details")]
        public Dictionary<string, object> Details { get; set; } = new();
        
        [JsonProperty("timestamp")]
        public DateTime Timestamp { get; set; } = DateTime.UtcNow;
    }

    public class NodeInfo
    {
        [JsonProperty("id")]
        public int Id { get; set; }
        
        [JsonProperty("hostname")]
        public string Hostname { get; set; } = string.Empty;
        
        [JsonProperty("ip_address")]
        public string IpAddress { get; set; } = string.Empty;
        
        [JsonProperty("group")]
        public string? Group { get; set; }
        
        [JsonProperty("status")]
        public string Status { get; set; } = string.Empty;
        
        [JsonProperty("last_seen")]
        public DateTime LastSeen { get; set; }
    }

    public class NodeRegistrationRequest
    {
        [JsonProperty("hostname")]
        public string Hostname { get; set; } = string.Empty;
        
        [JsonProperty("ip_address")]
        public string IpAddress { get; set; } = string.Empty;
        
        [JsonProperty("group")]
        public string? Group { get; set; }
    }

    public class HeartbeatRequest
    {
        [JsonProperty("hostname")]
        public string Hostname { get; set; } = string.Empty;
    }

    public class EventIngestRequest
    {
        [JsonProperty("node_id")]
        public int NodeId { get; set; }
        
        [JsonProperty("event_type")]
        public string EventType { get; set; } = string.Empty;
        
        [JsonProperty("severity")]
        public string Severity { get; set; } = string.Empty;
        
        [JsonProperty("details")]
        public Dictionary<string, object> Details { get; set; } = new();
    }
}
