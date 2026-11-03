constexpr int axisValue(int index)
{
    return (1 << index) - 1;
}

enum class Axis
{
    X = axisValue(0),
    Y = axisValue(1),
    Z = axisValue(2)
};

int main()
{
    Axis axis = Axis::Z;
    return static_cast<int>(axis);
}
