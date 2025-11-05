using System.Runtime.Versioning;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Options;
using Microsoft.Win32;

namespace AegisAgent
{
    [SupportedOSPlatform("windows")]
    public class RegistryMonitorCollector : EventCollectorBase
    {
        private readonly AgentConfiguration _config;
        private readonly IPolicyManager _policyManager;
        private Timer? _timer;
        private readonly ILogger<RegistryMonitorCollector> _logger;
        private readonly Dictionary<string, Dictionary<string, object?>> _lastRegistrySnapshot = new();

        public override string Name => "Registry Monitor";
        public override bool IsEnabled => _config.Collectors.RegistryMonitor.Enabled;

        // Critical registry paths to monitor
        private readonly List<RegistryPath> _monitoredPaths = new()
        {
            new RegistryPath(Registry.LocalMachine, @"SOFTWARE\Microsoft\Windows\CurrentVersion\Run", "Autorun (HKLM)"),
            new RegistryPath(Registry.LocalMachine, @"SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce", "RunOnce (HKLM)"),
            new RegistryPath(Registry.CurrentUser, @"SOFTWARE\Microsoft\Windows\CurrentVersion\Run", "Autorun (HKCU)"),
            new RegistryPath(Registry.CurrentUser, @"SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce", "RunOnce (HKCU)"),
            new RegistryPath(Registry.LocalMachine, @"SYSTEM\CurrentControlSet\Services", "Services"),
            new RegistryPath(Registry.LocalMachine, @"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon", "Winlogon"),
        };

        public RegistryMonitorCollector(
            IEventQueue eventQueue,
            ILogger<RegistryMonitorCollector> logger,
            INodeManager nodeManager,
            IPolicyManager policyManager,
            IOptions<AgentConfiguration> config)
            : base(eventQueue, nodeManager)
        {
            _config = config.Value;
            _logger = logger;
            _policyManager = policyManager;
        }

        public override Task StartAsync(CancellationToken cancellationToken)
        {
            if (!IsEnabled)
            {
                _logger.LogInformation("{Name} is disabled", Name);
                return Task.CompletedTask;
            }

            _logger.LogInformation("Starting {Name}...", Name);
            _logger.LogInformation("Monitoring {Count} registry paths", _monitoredPaths.Count);

            // Initial snapshot
            TakeRegistrySnapshot();

            var interval = TimeSpan.FromSeconds(_config.Collectors.RegistryMonitor.ScanIntervalSeconds);
            _timer = new Timer(MonitorRegistryChanges, null, interval, interval);

            return Task.CompletedTask;
        }

        private void TakeRegistrySnapshot()
        {
            foreach (var regPath in _monitoredPaths)
            {
                try
                {
                    using var key = regPath.Hive.OpenSubKey(regPath.SubKey);
                    if (key == null) continue;

                    var snapshot = new Dictionary<string, object?>();
                    foreach (var valueName in key.GetValueNames())
                    {
                        snapshot[valueName] = key.GetValue(valueName);
                    }

                    _lastRegistrySnapshot[regPath.FullPath] = snapshot;
                }
                catch (Exception ex)
                {
                    _logger.LogDebug(ex, "Could not read registry key: {Path}", regPath.FullPath);
                }
            }
        }

        private void MonitorRegistryChanges(object? state)
        {
            try
            {
                foreach (var regPath in _monitoredPaths)
                {
                    try
                    {
                        using var key = regPath.Hive.OpenSubKey(regPath.SubKey);
                        if (key == null) continue;

                        var currentSnapshot = new Dictionary<string, object?>();
                        foreach (var valueName in key.GetValueNames())
                        {
                            currentSnapshot[valueName] = key.GetValue(valueName);
                        }

                        // Get previous snapshot
                        if (!_lastRegistrySnapshot.TryGetValue(regPath.FullPath, out var previousSnapshot))
                        {
                            previousSnapshot = new Dictionary<string, object?>();
                        }

                        // Detect new values
                        foreach (var kvp in currentSnapshot)
                        {
                            if (!previousSnapshot.ContainsKey(kvp.Key))
                            {
                                _logger.LogWarning("New registry value detected: {Path}\\{ValueName} = {Value}",
                                    regPath.FullPath, kvp.Key, kvp.Value);

                                var details = new Dictionary<string, object>
                                {
                                    ["change_type"] = "value_added",
                                    ["registry_path"] = regPath.FullPath,
                                    ["value_name"] = kvp.Key,
                                    ["value_data"] = kvp.Value?.ToString() ?? "",
                                    ["description"] = regPath.Description,
                                    ["timestamp"] = DateTime.UtcNow
                                };

                                // Higher severity for protected keys
                                var severity = _policyManager.IsRegistryKeyProtected(regPath.FullPath) ? "high" : "medium";
                                QueueEvent("registry_value_added", severity, details);
                            }
                            else if (!Equals(previousSnapshot[kvp.Key], kvp.Value))
                            {
                                _logger.LogWarning("Registry value modified: {Path}\\{ValueName} = {Value}",
                                    regPath.FullPath, kvp.Key, kvp.Value);

                                var details = new Dictionary<string, object>
                                {
                                    ["change_type"] = "value_modified",
                                    ["registry_path"] = regPath.FullPath,
                                    ["value_name"] = kvp.Key,
                                    ["old_value"] = previousSnapshot[kvp.Key]?.ToString() ?? "",
                                    ["new_value"] = kvp.Value?.ToString() ?? "",
                                    ["description"] = regPath.Description,
                                    ["timestamp"] = DateTime.UtcNow
                                };

                                var severity = _policyManager.IsRegistryKeyProtected(regPath.FullPath) ? "high" : "medium";
                                QueueEvent("registry_value_modified", severity, details);
                            }
                        }

                        // Detect deleted values
                        foreach (var kvp in previousSnapshot)
                        {
                            if (!currentSnapshot.ContainsKey(kvp.Key))
                            {
                                _logger.LogWarning("Registry value deleted: {Path}\\{ValueName}",
                                    regPath.FullPath, kvp.Key);

                                var details = new Dictionary<string, object>
                                {
                                    ["change_type"] = "value_deleted",
                                    ["registry_path"] = regPath.FullPath,
                                    ["value_name"] = kvp.Key,
                                    ["old_value"] = kvp.Value?.ToString() ?? "",
                                    ["description"] = regPath.Description,
                                    ["timestamp"] = DateTime.UtcNow
                                };

                                var severity = _policyManager.IsRegistryKeyProtected(regPath.FullPath) ? "high" : "medium";
                                QueueEvent("registry_value_deleted", severity, details);
                            }
                        }

                        // Update snapshot
                        _lastRegistrySnapshot[regPath.FullPath] = currentSnapshot;
                    }
                    catch (Exception ex)
                    {
                        _logger.LogDebug(ex, "Error monitoring registry path: {Path}", regPath.FullPath);
                    }
                }
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error monitoring registry changes");
            }
        }

        public override Task StopAsync(CancellationToken cancellationToken)
        {
            _logger.LogInformation("Stopping {Name}...", Name);
            _timer?.Dispose();
            return Task.CompletedTask;
        }

        private class RegistryPath
        {
            public RegistryKey Hive { get; }
            public string SubKey { get; }
            public string Description { get; }
            public string FullPath => $"{GetHiveName(Hive)}\\{SubKey}";

            public RegistryPath(RegistryKey hive, string subKey, string description)
            {
                Hive = hive;
                SubKey = subKey;
                Description = description;
            }

            private static string GetHiveName(RegistryKey hive)
            {
                if (hive == Registry.LocalMachine) return "HKEY_LOCAL_MACHINE";
                if (hive == Registry.CurrentUser) return "HKEY_CURRENT_USER";
                if (hive == Registry.ClassesRoot) return "HKEY_CLASSES_ROOT";
                if (hive == Registry.Users) return "HKEY_USERS";
                if (hive == Registry.CurrentConfig) return "HKEY_CURRENT_CONFIG";
                return "UNKNOWN";
            }
        }
    }
}
