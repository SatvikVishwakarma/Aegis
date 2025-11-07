using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;
using Newtonsoft.Json;
using System.Net.Http.Headers;
using System.Text;

namespace AegisAgent
{
    public interface IApiClient
    {
        Task<NodeInfo> RegisterNodeAsync(NodeRegistrationRequest request);
        Task<NodeInfo> SendHeartbeatAsync(HeartbeatRequest request);
        Task SendEventAsync(EventIngestRequest request);
    }

    public class ApiClient : IApiClient
    {
        private readonly HttpClient _httpClient;
        private readonly string _apiUrl;
        private readonly string _apiKey;

        public ApiClient(IConfiguration configuration)
        {
            _apiUrl = configuration["Server:ApiUrl"] ?? throw new ArgumentNullException("Server:ApiUrl");
            _apiKey = configuration["Server:ApiKey"] ?? throw new ArgumentNullException("Server:ApiKey");

            _httpClient = new HttpClient
            {
                BaseAddress = new Uri(_apiUrl)
            };
            _httpClient.DefaultRequestHeaders.Add("X-API-Key", _apiKey);
        }

        public async Task<NodeInfo> RegisterNodeAsync(NodeRegistrationRequest request)
        {
            var content = new StringContent(
                JsonConvert.SerializeObject(request),
                Encoding.UTF8,
                "application/json"
            );

            var response = await _httpClient.PostAsync("/api/v1/nodes/register", content);
            response.EnsureSuccessStatusCode();

            var json = await response.Content.ReadAsStringAsync();
            return JsonConvert.DeserializeObject<NodeInfo>(json) 
                ?? throw new Exception("Failed to deserialize node info");
        }

        public async Task<NodeInfo> SendHeartbeatAsync(HeartbeatRequest request)
        {
            var content = new StringContent(
                JsonConvert.SerializeObject(request),
                Encoding.UTF8,
                "application/json"
            );

            var response = await _httpClient.PostAsync("/api/v1/nodes/heartbeat", content);
            response.EnsureSuccessStatusCode();

            var json = await response.Content.ReadAsStringAsync();
            return JsonConvert.DeserializeObject<NodeInfo>(json)
                ?? throw new Exception("Failed to deserialize node info");
        }

        public async Task SendEventAsync(EventIngestRequest request)
        {
            var content = new StringContent(
                JsonConvert.SerializeObject(request),
                Encoding.UTF8,
                "application/json"
            );

            var response = await _httpClient.PostAsync("/api/v1/logs/ingest", content);
            response.EnsureSuccessStatusCode();
        }
    }
}
