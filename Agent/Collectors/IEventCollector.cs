using Microsoft.Extensions.Logging;

namespace AegisAgent
{
    public interface IEventCollector
    {
        string Name { get; }
        bool IsEnabled { get; }
        Task StartAsync(CancellationToken cancellationToken);
        Task StopAsync(CancellationToken cancellationToken);
    }

    public abstract class EventCollectorBase : IEventCollector
    {
        protected readonly IEventQueue EventQueue;
        protected readonly INodeManager NodeManager;

        public abstract string Name { get; }
        public abstract bool IsEnabled { get; }

        protected EventCollectorBase(
            IEventQueue eventQueue,
            INodeManager nodeManager)
        {
            EventQueue = eventQueue;
            NodeManager = nodeManager;
        }

        public abstract Task StartAsync(CancellationToken cancellationToken);
        public abstract Task StopAsync(CancellationToken cancellationToken);

        protected void QueueEvent(string eventType, string severity, Dictionary<string, object> details)
        {
            var evt = new SecurityEvent
            {
                EventType = eventType,
                Severity = severity,
                Details = details,
                Timestamp = DateTime.UtcNow
            };

            EventQueue.Enqueue(evt);
        }
    }
}
