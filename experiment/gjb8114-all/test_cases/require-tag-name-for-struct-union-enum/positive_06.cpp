enum E_Color : unsigned char
{
    ColorRed = 1,
    ColorGreen = 2
};

int main()
{
    E_Color color = ColorGreen;
    return static_cast<int>(color);
}
