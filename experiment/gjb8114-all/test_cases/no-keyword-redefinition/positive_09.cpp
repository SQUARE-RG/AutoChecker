enum class TrafficLight
{
    red,
    yellow,
    green
};

int main()
{
    TrafficLight light = TrafficLight::yellow;
    return static_cast<int>(light);
}
