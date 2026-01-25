using System.Linq;
using WeightTracker.Api.SharedContracts;

namespace WeightTracker.Api.Endpoints.Status.Get;

internal static class StatusGetMappings
{
    public static StatusGetResponse ToResponse(this WeightTracker.Core.Models.Status data) => new(
        Today: new TodayResponse(data.Today.Date, data.Today.HasEntry, data.Today.Weight),
        Streak: new StreakResponse(data.Streak.Current, data.Streak.Longest),
        Adherence: data.Adherence.Select(a => new AdherenceResponseItem(a.Window, a.DaysWithEntry, a.DaysMissed)));
}
