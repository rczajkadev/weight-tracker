using System.Collections.Generic;

namespace WeightTracker.Core.Models;

public sealed record Status(Today Today, Streak Streak, IEnumerable<Adherence> Adherence)
{
    public static Status Create(IList<WeightData> data, DateOnly? referenceDate = null)
    {
        var today = referenceDate ?? DateOnly.FromDateTime(DateTime.UtcNow);

        return new Status(
            Today.Create(data, today),
            Streak.Create(data, referenceDate),
            [
                Models.Adherence.Create(data, 7, referenceDate),
                Models.Adherence.Create(data, 14, referenceDate),
                Models.Adherence.Create(data, 30, referenceDate)
            ]);
    }
}
