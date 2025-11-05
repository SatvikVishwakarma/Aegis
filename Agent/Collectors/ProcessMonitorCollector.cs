using System.Diagnostics;
using System.Runtime.Versioning;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Options;

namespace AegisAgent
{
    [SupportedOSPlatform("windows")]
    public class ProcessMonitorCollector : EventCollectorBase
    {
        private readonly AgentConfiguration _config;
        private Timer? _timer;
        private readonly HashSet<int> _trackedProcesses = new();
        private readonly ILogger<ProcessMonitorCollector> _logger;

        public override string Name => "Process Monitor";
        public override bool IsEnabled => _config.Collectors.ProcessMonitor.Enabled;

        public ProcessMonitorCollector(
            IEventQueue eventQueue,
            ILogger<ProcessMonitorCollector> logger,
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

            var interval = TimeSpan.FromSeconds(_config.Collectors.ProcessMonitor.ScanIntervalSeconds);
            _timer = new Timer(ScanProcesses, null, TimeSpan.Zero, interval);

            return Task.CompletedTask;
        }

        private void ScanProcesses(object? state)
        {
            try
            {
                var currentProcesses = Process.GetProcesses();
                var currentPids = new HashSet<int>(currentProcesses.Select(p => p.Id));

                // Detect new processes
                foreach (var process in currentProcesses)
                {
                    if (!_trackedProcesses.Contains(process.Id))
                    {
                        try
                        {
                            var details = new Dictionary<string, object>
                            {
                                ["process_id"] = process.Id,
                                ["process_name"] = process.ProcessName,
                                ["start_time"] = process.StartTime,
                            };

                            try
                            {
                                details["executable_path"] = process.MainModule?.FileName ?? "Unknown";
                                details["command_line"] = GetCommandLine(process.Id);
                            }
                            catch
                            {
                                // Access denied - process may be running with higher privileges
                                details["executable_path"] = "Access Denied";
                            }

                            QueueEvent("process_started", "low", details);
                        }
                        catch (Exception ex)
                        {
                            _logger.LogDebug(ex, "Could not get details for process {ProcessId}", process.Id);
                        }
                    }
                }

                // Update tracked processes
                var terminatedPids = _trackedProcesses.Except(currentPids).ToList();
                foreach (var pid in terminatedPids)
                {
                    var details = new Dictionary<string, object>
                    {
                        ["process_id"] = pid,
                        ["termination_time"] = DateTime.UtcNow
                    };

                    QueueEvent("process_terminated", "low", details);
                }

                _trackedProcesses.Clear();
                foreach (var pid in currentPids)
                {
                    _trackedProcesses.Add(pid);
                }

                foreach (var process in currentProcesses)
                {
                    process.Dispose();
                }
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error scanning processes");
            }
        }

        private string GetCommandLine(int processId)
        {
            try
            {
                using var searcher = new System.Management.ManagementObjectSearcher(
                    $"SELECT CommandLine FROM Win32_Process WHERE ProcessId = {processId}");

                foreach (System.Management.ManagementObject obj in searcher.Get())
                {
                    return obj["CommandLine"]?.ToString() ?? "";
                }
            }
            catch
            {
                // Ignore
            }

            return "";
        }

        [SupportedOSPlatform("windows")]
        public override Task StopAsync(CancellationToken cancellationToken)
        {
            _logger.LogInformation("Stopping {Name}...", Name);
            _timer?.Dispose();
            return Task.CompletedTask;
        }
    }
}
