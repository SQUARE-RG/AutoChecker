enum class Color { Red, Green, Blue };

int main()
{
    Color palette[] = { Color::Red, Color::Green, Color::Blue };
    unsigned int count = 3u;
    if (palette[0] == Color::Red)
    {
        return static_cast<int>(count);
    }
    return 0;
}
