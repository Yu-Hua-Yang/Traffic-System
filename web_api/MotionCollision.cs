namespace web_api
{
    public class MotionCollision
    {
        public DateOnly Date { get; set; }

        public String? PostalCode { get; set; }

        public required Detection Detection { get; set; }
    }

    public class Detection
    {
        public required string Type { get; set; }

        public bool Value { get; set; }
    }
}