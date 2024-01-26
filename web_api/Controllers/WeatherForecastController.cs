using System.Data;
using System.IdentityModel.Tokens.Jwt;
using Microsoft.AspNetCore.Mvc;

namespace web_api.Controllers;

[ApiController]
[Route("[controller]")]
public class WeatherForecastController : ControllerBase
{
    private static readonly string[] Summaries = new[]
    {
        "Freezing", "Bracing", "Chilly", "Cool", "Mild", "Warm", "Balmy", "Hot", "Sweltering", "Scorching"
    };

    private static readonly string[] PostalCodes = new []
    {
        "G9X 0P5", "T4G 3W5", "E8B 2G6", "L3M 3P8"
    };

    private readonly ILogger<WeatherForecastController> _logger;

    public WeatherForecastController(ILogger<WeatherForecastController> logger)
    {
        _logger = logger;
    }

    [HttpGet(Name = "GetWeatherForecast")]
    [ProducesResponseType(typeof(IEnumerable<WeatherForecast>), StatusCodes.Status200OK)]
    [ProducesResponseType(typeof(string), StatusCodes.Status400BadRequest)]
    [ProducesResponseType(typeof(string), StatusCodes.Status404NotFound)]
    [ProducesResponseType(typeof(string), StatusCodes.Status500InternalServerError)]
    [Produces("application/json")]
    public ActionResult<Object> Get(string token)
    {
      try {
        if(!validateJWTExpiry(token)){
          throw new DataException("Token was not valid");
        }

        String postalCode = PostalCodes[Random.Shared.Next(PostalCodes.Length)];
        int temperature = Random.Shared.Next(-40, 41);

        string[] conditionTypes = {
            "snowfall",
            "rain",
            "sunny",
            "cloudy"
        };
        string condition = conditionTypes[Random.Shared.Next(conditionTypes.Length)];

        string conditionIntensity = "n/a";
        if(condition.Equals("snowfall") || condition.Equals("rain")) {
            string[] intensities = {
                "light",
                "medium",
                "heavy"
            };
            conditionIntensity = intensities[Random.Shared.Next(intensities.Length)];
        }

        DateOnly date = DateOnly.FromDateTime(DateTime.Now);

        // return BadRequest("Error message for Bad Request (to be managed in a try/catch block)");
        return new WeatherForecast
        {
            PostalCode = postalCode,
            Temperature = temperature,
            Condition = new Condition {
                Type = condition,
                Intensity = conditionIntensity
            },
            Date = date
        };
      } catch (Exception e) {
        return BadRequest($"Exception found: {e}");
      }
    }

    public bool validateJWTExpiry(string inputToken){
      var token = new JwtSecurityToken(jwtEncodedString: inputToken);
      string expiry = token.Claims.First(c => c.Type == "exp").Value;
      var dtExpiry = DateTimeOffset.FromUnixTimeSeconds(long.Parse(expiry)).DateTime;
      return DateTime.Now < dtExpiry;
    }
}
