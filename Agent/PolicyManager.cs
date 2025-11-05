using System.Collections.Concurrent;
using System.Runtime.Versioning;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Options;

namespace AegisAgent
{
    public interface IPolicyManager
    {
        bool IsProcessBlacklisted(string processName);
        bool IsRegistryKeyProtected(string keyPath);
        void AddProcessBlacklist(string processName);
        void RemoveProcessBlacklist(string processName);
        void AddRegistryProtection(string keyPath);
        void RemoveRegistryProtection(string keyPath);
        List<string> GetBlacklistedProcesses();
        List<string> GetProtectedRegistryKeys();
    }

    [SupportedOSPlatform("windows")]
    public class PolicyManager : IPolicyManager
    {
        private readonly ConcurrentDictionary<string, bool> _blacklistedProcesses = new();
        private readonly ConcurrentDictionary<string, bool> _protectedRegistryKeys = new();
        private readonly ILogger<PolicyManager> _logger;
        private readonly AgentConfiguration _config;

        public PolicyManager(
            ILogger<PolicyManager> logger,
            IOptions<AgentConfiguration> config)
        {
            _logger = logger;
            _config = config.Value;
            InitializeDefaultPolicies();
        }

        private void InitializeDefaultPolicies()
        {
            // Default blacklisted processes (common malware/hacking tools)
            var defaultBlacklist = new[]
            {
                "mimikatz",
                "psexec",
                "netcat",
                "ncat",
                "nc",
                "procdump",
                "lazagne"
            };

            foreach (var process in defaultBlacklist)
            {
                _blacklistedProcesses.TryAdd(process.ToLower(), true);
            }

            // Default protected registry keys
            var defaultProtectedKeys = new[]
            {
                @"HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Run",
                @"HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce",
                @"HKEY_CURRENT_USER\SOFTWARE\Microsoft\Windows\CurrentVersion\Run",
                @"HKEY_CURRENT_USER\SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce",
                @"HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services"
            };

            foreach (var key in defaultProtectedKeys)
            {
                _protectedRegistryKeys.TryAdd(key.ToUpper(), true);
            }

            _logger.LogInformation("Initialized default policies: {ProcessCount} blacklisted processes, {KeyCount} protected registry keys",
                _blacklistedProcesses.Count, _protectedRegistryKeys.Count);
        }

        public bool IsProcessBlacklisted(string processName)
        {
            return _blacklistedProcesses.ContainsKey(processName.ToLower());
        }

        public bool IsRegistryKeyProtected(string keyPath)
        {
            var upperKey = keyPath.ToUpper();
            return _protectedRegistryKeys.Keys.Any(k => upperKey.StartsWith(k));
        }

        public void AddProcessBlacklist(string processName)
        {
            if (_blacklistedProcesses.TryAdd(processName.ToLower(), true))
            {
                _logger.LogInformation("Added process to blacklist: {ProcessName}", processName);
            }
        }

        public void RemoveProcessBlacklist(string processName)
        {
            if (_blacklistedProcesses.TryRemove(processName.ToLower(), out _))
            {
                _logger.LogInformation("Removed process from blacklist: {ProcessName}", processName);
            }
        }

        public void AddRegistryProtection(string keyPath)
        {
            if (_protectedRegistryKeys.TryAdd(keyPath.ToUpper(), true))
            {
                _logger.LogInformation("Added registry key protection: {KeyPath}", keyPath);
            }
        }

        public void RemoveRegistryProtection(string keyPath)
        {
            if (_protectedRegistryKeys.TryRemove(keyPath.ToUpper(), out _))
            {
                _logger.LogInformation("Removed registry key protection: {KeyPath}", keyPath);
            }
        }

        public List<string> GetBlacklistedProcesses()
        {
            return _blacklistedProcesses.Keys.ToList();
        }

        public List<string> GetProtectedRegistryKeys()
        {
            return _protectedRegistryKeys.Keys.ToList();
        }
    }
}
