using System.Security.Claims;

namespace WeightTracker.Api.Extensions;

internal static class HttpContextExtensions
{
    public static string? GetUserId(this HttpContext context) => context.User.FindFirstValue(ClaimTypes.NameIdentifier);
}
