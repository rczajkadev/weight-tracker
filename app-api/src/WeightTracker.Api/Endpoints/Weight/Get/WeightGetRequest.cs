using FluentValidation;

namespace WeightTracker.Api.Endpoints.Weight.Get;

internal sealed record WeightGetRequest(string? DateFrom, string? DateTo);

internal sealed class WeightGetRequestValidator : Validator<WeightGetRequest>
{
    public WeightGetRequestValidator()
    {
        RuleFor(r => r.DateFrom)
            .Must(date => string.IsNullOrWhiteSpace(date) || date.IsValidDomainDateFormat())
            .WithMessage("Invalid date format");

        RuleFor(r => r.DateTo)
            .Must(date => string.IsNullOrWhiteSpace(date) || date.IsValidDomainDateFormat())
            .WithMessage("Invalid date format");
    }
}
