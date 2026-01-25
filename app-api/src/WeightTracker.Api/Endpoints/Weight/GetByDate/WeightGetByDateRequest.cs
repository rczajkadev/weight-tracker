using FluentValidation;

namespace WeightTracker.Api.Endpoints.Weight.GetByDate;

internal sealed record WeightGetByDateRequest(string Date);

internal sealed class WeightGetByDateRequestValidator : Validator<WeightGetByDateRequest>
{
    public WeightGetByDateRequestValidator()
    {
        RuleFor(r => r.Date)
            .Must(date => string.IsNullOrWhiteSpace(date) || date.IsValidDomainDateFormat())
            .WithMessage("Invalid date format");
    }
}
