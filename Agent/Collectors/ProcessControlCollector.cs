using System.Diagnostics;
using System.Runtime.InteropServices;
using System.Runtime.Versioning;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Options;

namespace AegisAgent
{
    [SupportedOSPlatform("windows")]
    public class ProcessControlCollector : EventCollectorBase
    {
        private readonly AgentConfiguration _config;
        private readonly IPolicyManager _policyManager;
        private Timer? _timer;
        private readonly ILogger<ProcessControlCollector> _logger;

        // Win32 API for process suspension
        [DllImport("kernel32.dll")]
        private static extern IntPtr OpenThread(int dwDesiredAccess, bool bInheritHandle, uint dwThreadId);

        [DllImport("kernel32.dll")]
        private static extern uint SuspendThread(IntPtr hThread);

        [DllImport("kernel32.dll")]
        private static extern int ResumeThread(IntPtr hThread);

        [DllImport("kernel32.dll", SetLastError = true)]
        private static extern bool CloseHandle(IntPtr hHandle);

        private const int THREAD_SUSPEND_RESUME = 0x0002;

        public override string Name => "Process Control";
        public override bool IsEnabled => _config.Collectors.ProcessControl.Enabled;

        public ProcessControlCollector(
            IEventQueue eventQueue,
            ILogger<ProcessControlCollector> logger,
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
            _logger.LogWarning("Process Control is active - blacklisted processes will be terminated");

            var interval = TimeSpan.FromSeconds(_config.Collectors.ProcessControl.ScanIntervalSeconds);
            _timer = new Timer(ScanAndControlProcesses, null, TimeSpan.Zero, interval);

            return Task.CompletedTask;
        }

        private void ScanAndControlProcesses(object? state)
        {
            try
            {
                var processes = Process.GetProcesses();

                foreach (var process in processes)
                {
                    try
                    {
                        var processName = process.ProcessName.ToLower();

                        // Check if process is blacklisted
                        if (_policyManager.IsProcessBlacklisted(processName))
                        {
                            _logger.LogWarning("Blacklisted process detected: {ProcessName} (PID: {ProcessId})",
                                processName, process.Id);

                            var action = _config.Collectors.ProcessControl.Action;

                            switch (action.ToLower())
                            {
                                case "kill":
                                    KillProcess(process);
                                    break;
                                case "suspend":
                                    SuspendProcess(process);
                                    break;
                                case "alert":
                                    AlertOnProcess(process);
                                    break;
                                default:
                                    _logger.LogWarning("Unknown action: {Action}", action);
                                    break;
                            }
                        }
                    }
                    catch (Exception ex)
                    {
                        _logger.LogDebug(ex, "Could not check process {ProcessId}", process.Id);
                    }
                    finally
                    {
                        process.Dispose();
                    }
                }
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error scanning processes for control");
            }
        }

        private void KillProcess(Process process)
        {
            try
            {
                var processName = process.ProcessName;
                var processId = process.Id;

                process.Kill(true); // Kill entire process tree
                _logger.LogWarning("KILLED blacklisted process: {ProcessName} (PID: {ProcessId})",
                    processName, processId);

                var details = new Dictionary<string, object>
                {
                    ["action"] = "kill",
                    ["process_name"] = processName,
                    ["process_id"] = processId,
                    ["reason"] = "blacklisted",
                    ["timestamp"] = DateTime.UtcNow
                };

                QueueEvent("process_terminated_by_policy", "high", details);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to kill process {ProcessId}", process.Id);
            }
        }

        private void SuspendProcess(Process process)
        {
            try
            {
                foreach (ProcessThread thread in process.Threads)
                {
                    var threadHandle = OpenThread(THREAD_SUSPEND_RESUME, false, (uint)thread.Id);
                    if (threadHandle != IntPtr.Zero)
                    {
                        SuspendThread(threadHandle);
                        CloseHandle(threadHandle);
                    }
                }

                _logger.LogWarning("SUSPENDED blacklisted process: {ProcessName} (PID: {ProcessId})",
                    process.ProcessName, process.Id);

                var details = new Dictionary<string, object>
                {
                    ["action"] = "suspend",
                    ["process_name"] = process.ProcessName,
                    ["process_id"] = process.Id,
                    ["reason"] = "blacklisted",
                    ["timestamp"] = DateTime.UtcNow
                };

                QueueEvent("process_suspended_by_policy", "high", details);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to suspend process {ProcessId}", process.Id);
            }
        }

        private void AlertOnProcess(Process process)
        {
            _logger.LogWarning("ALERT: Blacklisted process detected: {ProcessName} (PID: {ProcessId})",
                process.ProcessName, process.Id);

            var details = new Dictionary<string, object>
            {
                ["action"] = "alert",
                ["process_name"] = process.ProcessName,
                ["process_id"] = process.Id,
                ["reason"] = "blacklisted",
                ["timestamp"] = DateTime.UtcNow
            };

            try
            {
                details["executable_path"] = process.MainModule?.FileName ?? "Unknown";
            }
            catch
            {
                details["executable_path"] = "Access Denied";
            }

            QueueEvent("blacklisted_process_detected", "critical", details);
        }

        public override Task StopAsync(CancellationToken cancellationToken)
        {
            _logger.LogInformation("Stopping {Name}...", Name);
            _timer?.Dispose();
            return Task.CompletedTask;
        }
    }
}
