namespace AegisAgent
{
    public class AgentConfiguration
    {
        public ServerConfig Server { get; set; } = new();
        public NodeConfig Node { get; set; } = new();
        public MonitoringConfig Monitoring { get; set; } = new();
        public CollectorsConfig Collectors { get; set; } = new();
    }

    public class ServerConfig
    {
        public string ApiUrl { get; set; } = string.Empty;
        public string ApiKey { get; set; } = string.Empty;
    }

    public class NodeConfig
    {
        public string Hostname { get; set; } = "auto";
        public string IpAddress { get; set; } = "auto";
        public string Group { get; set; } = string.Empty;
    }

    public class MonitoringConfig
    {
        public int HeartbeatIntervalSeconds { get; set; } = 60;
        public int EventBatchSize { get; set; } = 10;
        public int EventBatchIntervalSeconds { get; set; } = 5;
        public int StatusCheckIntervalSeconds { get; set; } = 30;
    }

    public class CollectorsConfig
    {
        public ProcessMonitorConfig ProcessMonitor { get; set; } = new();
        public NetworkMonitorConfig NetworkMonitor { get; set; } = new();
    }

    public class ProcessMonitorConfig
    {
        public bool Enabled { get; set; } = true;
        public int ScanIntervalSeconds { get; set; } = 10;
    }

    public class NetworkMonitorConfig
    {
        public bool Enabled { get; set; } = true;
        public int ScanIntervalSeconds { get; set; } = 30;
    }
}
