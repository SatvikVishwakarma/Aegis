using System.Net;
using System.Net.NetworkInformation;
using System.Net.Sockets;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Options;

namespace AegisAgent
{
    public interface INodeManager
    {
        string Hostname { get; }
        string IpAddress { get; }
        string? Group { get; }
        int? NodeId { get; }
        Task RegisterAsync();
        Task SendHeartbeatAsync();
    }

    public class NodeManager : INodeManager
    {
        private readonly IApiClient _apiClient;
        private readonly ILogger<NodeManager> _logger;
        private readonly AgentConfiguration _config;

        public string Hostname { get; private set; }
        public string IpAddress { get; private set; }
        public string? Group { get; private set; }
        public int? NodeId { get; private set; }

        public NodeManager(
            IApiClient apiClient, 
            ILogger<NodeManager> logger,
            IOptions<AgentConfiguration> config)
        {
            _apiClient = apiClient;
            _logger = logger;
            _config = config.Value;

            Hostname = DetermineHostname();
            IpAddress = DetermineIpAddress();
            Group = _config.Node.Group;
        }

        private string DetermineHostname()
        {
            var configHostname = _config.Node.Hostname;
            if (configHostname != "auto")
                return configHostname;

            return Dns.GetHostName();
        }

        private string DetermineIpAddress()
        {
            var configIp = _config.Node.IpAddress;
            if (configIp != "auto")
                return configIp;

            try
            {
                // Get the first non-loopback IPv4 address
                var host = Dns.GetHostEntry(Dns.GetHostName());
                foreach (var ip in host.AddressList)
                {
                    if (ip.AddressFamily == AddressFamily.InterNetwork && 
                        !IPAddress.IsLoopback(ip))
                    {
                        return ip.ToString();
                    }
                }
            }
            catch (Exception ex)
            {
                _logger.LogWarning(ex, "Failed to auto-detect IP address, using 127.0.0.1");
            }

            return "127.0.0.1";
        }

        public async Task RegisterAsync()
        {
            try
            {
                _logger.LogInformation("Registering node with server...");
                _logger.LogInformation("Hostname: {Hostname}", Hostname);
                _logger.LogInformation("IP Address: {IpAddress}", IpAddress);
                _logger.LogInformation("Group: {Group}", Group ?? "None");

                var request = new NodeRegistrationRequest
                {
                    Hostname = Hostname,
                    IpAddress = IpAddress,
                    Group = Group
                };

                var nodeInfo = await _apiClient.RegisterNodeAsync(request);
                NodeId = nodeInfo.Id;

                _logger.LogInformation("Successfully registered! Node ID: {NodeId}", NodeId);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to register node with server");
                throw;
            }
        }

        public async Task SendHeartbeatAsync()
        {
            try
            {
                var request = new HeartbeatRequest { Hostname = Hostname };
                await _apiClient.SendHeartbeatAsync(request);
                _logger.LogDebug("Heartbeat sent successfully");
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to send heartbeat");
                throw;
            }
        }
    }
}
