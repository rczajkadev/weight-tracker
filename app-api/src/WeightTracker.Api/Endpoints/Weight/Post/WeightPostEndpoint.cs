using System.Globalization;
using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.OutputCaching;
using WeightTracker.Api.Cache;
using WeightTracker.Api.Extensions;
using WeightTracker.Api.Handlers;

namespace WeightTracker.Api.Endpoints.Weight.Post;

internal sealed class WeightPostEndpoint : Endpoint<WeightPostRequest, IResult>
{
    public required CurrentUser CurrentUser { get; init; }

    public required IOutputCacheStore Cache { get; init; }

    public override void Configure()
    {
        Post("api/weight");
        Description(builder => builder
            .WithName("AddWeight")
            .Produces(StatusCodes.Status200OK)
            .ProducesWriteCommonProblems());
    }

    public override async Task<IResult> ExecuteAsync(WeightPostRequest request, CancellationToken ct)
    {
        if (string.IsNullOrWhiteSpace(CurrentUser.Id))
            return Results.Unauthorized();

        var (weight, date) = request;
        var command = new AddWeightData(CurrentUser.Id, GetDate(date), weight);
        var result = await command.ExecuteAsync(ct);

        await Cache.EvictByUidAsync(CurrentUser.Id, ct);
        return result.Match(() => Results.Ok(), ErrorsService.HandleError);
    }

    private static DateOnly GetDate(string? date)
    {
        return string.IsNullOrWhiteSpace(date)
            ? DateOnly.FromDateTime(DateTime.UtcNow)
            : DateOnly.Parse(date, CultureInfo.InvariantCulture);
    }
}
