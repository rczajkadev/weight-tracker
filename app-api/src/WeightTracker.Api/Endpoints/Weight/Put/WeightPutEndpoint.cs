using System.Globalization;
using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.OutputCaching;
using WeightTracker.Api.Cache;
using WeightTracker.Api.Extensions;
using WeightTracker.Api.Handlers;

namespace WeightTracker.Api.Endpoints.Weight.Put;

internal sealed class WeightPutEndpoint : Endpoint<WeightPutRequest, IResult>
{
    public required CurrentUser CurrentUser { get; init; }

    public required IOutputCacheStore Cache { get; init; }

    public override void Configure()
    {
        Put("api/weight/{Date}");
        Description(builder => builder
            .WithName("UpdateWeight")
            .Produces(StatusCodes.Status200OK)
            .ProducesWriteCommonProblems());
    }

    public override async Task<IResult> ExecuteAsync(WeightPutRequest request, CancellationToken ct)
    {
        if (string.IsNullOrWhiteSpace(CurrentUser.Id))
            return Results.Unauthorized();

        var (date, weight) = request;
        var command = new UpdateWeightData(
            UserId: CurrentUser.Id,
            Date: DateOnly.Parse(date, CultureInfo.InvariantCulture),
            Weight: weight);
        var result = await command.ExecuteAsync(ct);

        await Cache.EvictByUidAsync(CurrentUser.Id, ct);
        return result.Match(() => Results.Ok(), ErrorsService.HandleError);
    }
}
