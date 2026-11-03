enum class Color
{
    Red,
    Green,
    Blue
};

int branch_on_enum(Color color)
{
    if (color == Color::Red)
    {
        return 1;
    }
    else
    {
        return 0;
    }
}

int main()
{
    return branch_on_enum(Color::Red) + branch_on_enum(Color::Green);
}
