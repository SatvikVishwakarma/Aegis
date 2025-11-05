using System.Net.NetworkInformation;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Options;

namespace AegisAgent
{
    public class NetworkMonitorCollector : EventCollectorBase
    {
        private readonly AgentConfiguration _config;
        private Timer? _timer;
        private readonly HashSet<string> _trackedConnections = new();
        private readonly ILogger<NetworkMonitorCollector> _logger;

        public override string Name => "Network Monitor";
        public override bool IsEnabled => _config.Collectors.NetworkMonitor.Enabled;

        public NetworkMonitorCollector(
            IEventQueue eventQueue,
            ILogger<NetworkMonitorCollector> logger,
            INodeManager nodeManager,
            IOptions<AgentConfiguration> config)
            : base(eventQueue, nodeManager)
        {
            _config = config.Value;
            _logger = logger;
        }

        public override Task StartAsync(CancellationToken cancellationToken)
        {
            if (!IsEnabled)
            {
                _logger.LogInformation("{Name} is disabled", Name);
                return Task.CompletedTask;
            }

            _logger.LogInformation("Starting {Name}...", Name);

            var interval = TimeSpan.FromSeconds(_config.Collectors.NetworkMonitor.ScanIntervalSeconds);
            _timer = new Timer(ScanNetworkConnections, null, TimeSpan.Zero, interval);

            return Task.CompletedTask;
        }

        private void ScanNetworkConnections(object? state)
        {
            try
            {
                var ipGlobalProperties = IPGlobalProperties.GetIPGlobalProperties();
                var tcpConnections = ipGlobalProperties.GetActiveTcpConnections();

                var currentConnections = new HashSet<string>();

                foreach (var connection in tcpConnections)
                {
                    // Only track established connections
                    if (connection.State != TcpState.Established)
                        continue;

                    var connectionKey = $"{connection.LocalEndPoint}-{connection.RemoteEndPoint}";
                    currentConnections.Add(connectionKey);

                    // New connection detected
                    if (!_trackedConnections.Contains(connectionKey))
                    {
                        var details = new Dictionary<string, object>
                        {
                            ["direction"] = "established",
                            ["protocol"] = "tcp",
                            ["local_address"] = connection.LocalEndPoint.Address.ToString(),
                            ["local_port"] = connection.LocalEndPoint.Port,
                            ["remote_address"] = connection.RemoteEndPoint.Address.ToString(),
                            ["remote_port"] = connection.RemoteEndPoint.Port,
                            ["state"] = connection.State.ToString(),
                            ["timestamp"] = DateTime.UtcNow
                        };

                        // Determine severity based on remote port
                        var severity = DetermineSeverity(connection.RemoteEndPoint.Port);

                        QueueEvent("network_connection", severity, details);
                    }
                }

                // Update tracked connections
                _trackedConnections.Clear();
                foreach (var conn in currentConnections)
                {
                    _trackedConnections.Add(conn);
                }
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error scanning network connections");
            }
        }

        private string DetermineSeverity(int port)
        {
            // Flag suspicious ports
            var suspiciousPorts = new[] { 4444, 5555, 6666, 1337, 31337 };
            if (suspiciousPorts.Contains(port))
                return "high";

            // Common service ports are low severity
            var commonPorts = new[] { 80, 443, 22, 21, 25, 53, 3389 };
            if (commonPorts.Contains(port))
                return "low";

            return "medium";
        }

        public override Task StopAsync(CancellationToken cancellationToken)
        {
            _logger.LogInformation("Stopping {Name}...", Name);
            _timer?.Dispose();
            return Task.CompletedTask;
        }
    }
}
