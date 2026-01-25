using System.Globalization;
using System.Linq;
using WeightTracker.Api.Handlers;

namespace WeightTracker.Api.Endpoints.Weight.GetByDate;

internal static class WeightGetByDateMappings
{
    public static GetWeightData ToCommand(this WeightGetByDateRequest request, string userId)
    {
        var date = string.IsNullOrWhiteSpace(request.Date)
            ? DateOnly.MinValue
            : DateOnly.Parse(request.Date, CultureInfo.InvariantCulture);

        return new GetWeightData(userId, date, date);
    }

    public static WeightGetByDateResponse ToResponse(this WeightDataGroup data) => new()
    {
        UserId = data.UserId,
        Date = data.Data.First().Date.ToDomainDateString(),
        Weight = data.Data.First().Weight
    };
}
