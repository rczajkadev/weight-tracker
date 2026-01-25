using System.Globalization;
using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.OutputCaching;
using WeightTracker.Api.Cache;
using WeightTracker.Api.Extensions;
using WeightTracker.Api.Handlers;

namespace WeightTracker.Api.Endpoints.Weight.Delete;

internal sealed class WeightDeleteEndpoint : Endpoint<WeightDeleteRequest, IResult>
{
    public required CurrentUser CurrentUser { get; init; }

    public required IOutputCacheStore Cache { get; init; }

    public override void Configure()
    {
        Delete("api/weight/{Date}");
        Description(builder => builder
            .WithName("DeleteWeight")
            .Produces(StatusCodes.Status200OK)
            .ProducesWriteCommonProblems());
    }

    public override async Task<IResult> ExecuteAsync(WeightDeleteRequest request, CancellationToken ct)
    {
        if (string.IsNullOrWhiteSpace(CurrentUser.Id))
            return Results.Unauthorized();

        var command = new RemoveWeightData(
            UserId: CurrentUser.Id,
            Date: DateOnly.Parse(request.Date, CultureInfo.InvariantCulture));
        var result = await command.ExecuteAsync(ct);

        await Cache.EvictByUidAsync(CurrentUser.Id, ct);
        return result.Match(() => Results.Ok(), ErrorsService.HandleError);
    }
}
