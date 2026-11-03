enum Color
{
    RED = 011 /* octal */,
    GREEN = 2,
    BLUE = 3
};

int main()
{
    Color color = GREEN;
    return static_cast<int>(color);
}
