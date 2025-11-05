using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Options;

namespace AegisAgent
{
    public class AgentService : BackgroundService
    {
        private readonly INodeManager _nodeManager;
        private readonly IApiClient _apiClient;
        private readonly IEventQueue _eventQueue;
        private readonly IEnumerable<IEventCollector> _collectors;
        private readonly ILogger<AgentService> _logger;
        private readonly AgentConfiguration _config;

        public AgentService(
            INodeManager nodeManager,
            IApiClient apiClient,
            IEventQueue eventQueue,
            IEnumerable<IEventCollector> collectors,
            ILogger<AgentService> logger,
            IOptions<AgentConfiguration> config)
        {
            _nodeManager = nodeManager;
            _apiClient = apiClient;
            _eventQueue = eventQueue;
            _collectors = collectors;
            _logger = logger;
            _config = config.Value;
        }

        protected override async Task ExecuteAsync(CancellationToken stoppingToken)
        {
            try
            {
                // Register node with server
                await _nodeManager.RegisterAsync();

                // Start all enabled collectors
                foreach (var collector in _collectors)
                {
                    await collector.StartAsync(stoppingToken);
                }

                // Start background tasks
                var heartbeatTask = HeartbeatLoopAsync(stoppingToken);
                var eventProcessorTask = ProcessEventsAsync(stoppingToken);

                await Task.WhenAll(heartbeatTask, eventProcessorTask);
            }
            catch (Exception ex)
            {
                _logger.LogCritical(ex, "Fatal error in agent service");
                throw;
            }
        }

        private async Task HeartbeatLoopAsync(CancellationToken stoppingToken)
        {
            var interval = TimeSpan.FromSeconds(_config.Monitoring.HeartbeatIntervalSeconds);

            while (!stoppingToken.IsCancellationRequested)
            {
                try
                {
                    await _nodeManager.SendHeartbeatAsync();
                    await Task.Delay(interval, stoppingToken);
                }
                catch (OperationCanceledException)
                {
                    break;
                }
                catch (Exception ex)
                {
                    _logger.LogError(ex, "Error sending heartbeat, will retry...");
                    await Task.Delay(TimeSpan.FromSeconds(10), stoppingToken);
                }
            }
        }

        private async Task ProcessEventsAsync(CancellationToken stoppingToken)
        {
            var interval = TimeSpan.FromSeconds(_config.Monitoring.EventBatchIntervalSeconds);

            while (!stoppingToken.IsCancellationRequested)
            {
                try
                {
                    await Task.Delay(interval, stoppingToken);

                    var batchSize = _config.Monitoring.EventBatchSize;
                    var events = new List<SecurityEvent>();

                    // Dequeue up to batch size
                    for (int i = 0; i < batchSize; i++)
                    {
                        var evt = _eventQueue.Dequeue();
                        if (evt == null) break;
                        events.Add(evt);
                    }

                    if (events.Count == 0)
                        continue;

                    // Send events to server
                    foreach (var evt in events)
                    {
                        try
                        {
                            if (!_nodeManager.NodeId.HasValue)
                            {
                                _logger.LogWarning("Node not registered, cannot send events");
                                break;
                            }

                            var request = new EventIngestRequest
                            {
                                NodeId = _nodeManager.NodeId.Value,
                                EventType = evt.EventType,
                                Severity = evt.Severity,
                                Details = evt.Details
                            };

                            await _apiClient.SendEventAsync(request);
                            _logger.LogDebug("Event sent: {EventType}", evt.EventType);
                        }
                        catch (Exception ex)
                        {
                            _logger.LogError(ex, "Failed to send event {EventType}", evt.EventType);
                            // Re-queue failed event
                            _eventQueue.Enqueue(evt);
                        }
                    }

                    if (events.Count > 0)
                    {
                        _logger.LogInformation("Processed {Count} events", events.Count);
                    }
                }
                catch (OperationCanceledException)
                {
                    break;
                }
                catch (Exception ex)
                {
                    _logger.LogError(ex, "Error processing events");
                }
            }
        }

        public override async Task StopAsync(CancellationToken cancellationToken)
        {
            _logger.LogInformation("Shutting down agent...");

            // Stop all collectors
            foreach (var collector in _collectors)
            {
                await collector.StopAsync(cancellationToken);
            }

            await base.StopAsync(cancellationToken);
            _logger.LogInformation("Agent stopped");
        }
    }
}
