using WeightTracker.Api.SharedContracts;

namespace WeightTracker.Api.Endpoints.Weight.Get;

internal sealed class WeightGetResponse
{
    public string UserId { get; init; } = null!;

    public TodayResponse Today { get; init; } = null!;

    public StatsResponse Stats { get; init; } = null!;

    public IEnumerable<WeightResponseItem> Data { get; init; } = null!;
}

internal sealed record StatsResponse(decimal Avg, decimal Max, decimal Min);

internal sealed record WeightResponseItem(string Date, decimal Weight);
