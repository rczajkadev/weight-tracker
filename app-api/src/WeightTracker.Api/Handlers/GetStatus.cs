namespace WeightTracker.Api.Handlers;

internal sealed record GetStatus(string UserId) : ICommand<Result<Status>>;

internal sealed class GetStatusHandler(IRepository repository) : ICommandHandler<GetStatus, Result<Status>>
{
    public async Task<Result<Status>> ExecuteAsync(GetStatus command, CancellationToken ct)
    {
        var filter = new WeightDataFilter(command.UserId);
        var dataGroup = await repository.GetAsync(filter, ct);
        return Status.Create([.. dataGroup.Data]);
    }
}
