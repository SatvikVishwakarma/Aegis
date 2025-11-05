using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;
using System.Runtime.Versioning;

namespace AegisAgent
{
    [SupportedOSPlatform("windows")]
    class Program
    {
        static async Task Main(string[] args)
        {
            var host = Host.CreateDefaultBuilder(args)
                .ConfigureAppConfiguration((context, config) =>
                {
                    config.AddJsonFile("appsettings.json", optional: false, reloadOnChange: true);
                })
                .ConfigureServices((context, services) =>
                {
                    // Register configuration
                    services.Configure<AgentConfiguration>(context.Configuration);

                    // Register services
                    services.AddSingleton<IApiClient, ApiClient>();
                    services.AddSingleton<INodeManager, NodeManager>();
                    services.AddSingleton<IEventQueue, EventQueue>();

                    // Register collectors
                    services.AddSingleton<IEventCollector, ProcessMonitorCollector>();
                    services.AddSingleton<IEventCollector, NetworkMonitorCollector>();

                    // Register hosted service
                    services.AddHostedService<AgentService>();
                })
                .ConfigureLogging((context, logging) =>
                {
                    logging.ClearProviders();
                    logging.AddConsole();
                })
                .Build();

            Console.WriteLine("===========================================");
            Console.WriteLine("Aegis Security Monitoring Agent");
            Console.WriteLine("===========================================");
            Console.WriteLine();

            await host.RunAsync();
        }
    }
}
