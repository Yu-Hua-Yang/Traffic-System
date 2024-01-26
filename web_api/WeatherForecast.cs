namespace web_api;

public class WeatherForecast
{
    public DateOnly Date { get; set; }

    public int Temperature { get; set; }

    public String? PostalCode { get; set; }

    public Condition? Condition { get; set; }
}

public class Condition
{
    public String? Type { get; set; }
    public String? Intensity { get; set; }
}