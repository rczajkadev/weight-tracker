namespace WeightTracker.Api.SharedContracts;

internal sealed record TodayResponse(DateOnly Date, bool HasEntry, decimal? Weight);
