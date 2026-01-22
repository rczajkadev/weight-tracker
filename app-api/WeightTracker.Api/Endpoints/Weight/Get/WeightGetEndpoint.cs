using Microsoft.AspNetCore.Builder;
using WeightTracker.Api.Cache;
using WeightTracker.Api.Extensions;

namespace WeightTracker.Api.Endpoints.Weight.Get;

internal sealed class WeightGetEndpoint : Endpoint<WeightGetRequest, IResult>
{
    public required CurrentUser CurrentUser { get; init; }

    public override void Configure()
    {
        Get("api/weight");
        Options(builder => builder.SetCustomCache());
        Description(builder => builder
            .WithName("GetWeight")
            .Produces<WeightGetResponse>()
            .ProducesCommonProblems());
    }

    public override async Task<IResult> ExecuteAsync(WeightGetRequest request, CancellationToken ct)
    {
        if (string.IsNullOrWhiteSpace(CurrentUser.Id))
            return Results.Unauthorized();

        var command = request.ToCommand(CurrentUser.Id);
        var result = await command.ExecuteAsync(ct);

        return result.Match(d => Results.Ok(d.ToResponse()), ErrorsService.HandleError);
    }
}
