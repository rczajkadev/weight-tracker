namespace WeightTracker.Api.Endpoints.Weight.GetByDate;

internal sealed class WeightGetByDateResponse
{
    public string UserId { get; init; } = null!;

    public string Date { get; init; } = null!;

    public decimal Weight { get; init; }
}
