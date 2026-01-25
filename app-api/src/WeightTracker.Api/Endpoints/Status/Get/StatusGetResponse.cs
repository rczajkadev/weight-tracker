using WeightTracker.Api.SharedContracts;

namespace WeightTracker.Api.Endpoints.Status.Get;

internal sealed record StatusGetResponse(TodayResponse Today, StreakResponse Streak, IEnumerable<AdherenceResponseItem> Adherence);

internal sealed record StreakResponse(int Current, int Longest);

internal sealed record AdherenceResponseItem(int Window, int DaysWithEntry, int DaysMissed);
