using System.Collections.Concurrent;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Options;

namespace AegisAgent
{
    public interface IEventQueue
    {
        void Enqueue(SecurityEvent evt);
        SecurityEvent? Dequeue();
        int Count { get; }
    }

    public class EventQueue : IEventQueue
    {
        private readonly ConcurrentQueue<SecurityEvent> _queue = new();
        private readonly ILogger<EventQueue> _logger;

        public int Count => _queue.Count;

        public EventQueue(ILogger<EventQueue> logger)
        {
            _logger = logger;
        }

        public void Enqueue(SecurityEvent evt)
        {
            _queue.Enqueue(evt);
            _logger.LogDebug("Event queued: {EventType} ({Severity})", evt.EventType, evt.Severity);
        }

        public SecurityEvent? Dequeue()
        {
            _queue.TryDequeue(out var evt);
            return evt;
        }
    }
}
