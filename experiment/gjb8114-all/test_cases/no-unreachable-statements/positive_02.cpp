int clamp(int value)
{
    if (value < 0)
    {
        return 0;
    }
    if (value > 10)
    {
        return 10;
    }
    return value;
}

int main()
{
    return clamp(5);
}
