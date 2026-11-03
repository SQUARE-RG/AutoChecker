int safe_divide(int numerator, int denominator)
{
    try
    {
        if (denominator == 0)
        {
            throw 1;
        }
        return numerator / denominator;
    }
    catch (int)
    {
        return 0;
    }
}

int main()
{
    return safe_divide(10, 2);
}
