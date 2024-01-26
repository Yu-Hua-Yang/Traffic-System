using System.Runtime.CompilerServices;
using System.IdentityModel.Tokens.Jwt;
using Microsoft.AspNetCore.Mvc;
using System.Data;

namespace web_api.Controllers;

[ApiController]
[Route("[controller]")]

public class MotionCollisionController :ControllerBase
{
 private static Random random = new Random();

 private static readonly string[] PostalCodes = new []
 {
        "G9X 0P5", "T4G 3W5", "E8B 2G6", "L3M 3P8"
 };

 private readonly ILogger<MotionCollisionController> _logger;

 public MotionCollisionController(ILogger<MotionCollisionController> logger)
 {
     _logger = logger;
 }

 [HttpGet(Name = "GetMotionCollision")]
 [ProducesResponseType(typeof(IEnumerable<MotionCollision>), StatusCodes.Status200OK)]
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
     string postalCode = PostalCodes[Random.Shared.Next(PostalCodes.Length)];

     string[] detectionTypes = { "motion", "collision" };
     string detectionType = detectionTypes[Random.Shared.Next(detectionTypes.Length)];
     bool detectionValue = Random.Shared.Next(2) == 0; // Random true or false

     DateOnly date = DateOnly.FromDateTime(DateTime.Now);

     return new MotionCollision
     {
         Date = date,
         PostalCode = postalCode,
         Detection = new Detection
         {
             Type = detectionType,
             Value = detectionValue
         }
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