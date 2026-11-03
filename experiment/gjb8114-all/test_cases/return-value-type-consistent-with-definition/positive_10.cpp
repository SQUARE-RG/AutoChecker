enum Color
{
    kRed = 1,
    kGreen = 2
};

Color color_value()
{
    Color color = kGreen;
    return color;
}

int main()
{
    Color color = color_value();
    return (color == kGreen) ? 0 : 1;
}
