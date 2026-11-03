static int scale(int value)
{
    return value * 2;
}

int main()
{
    struct Calculator
    {
        int apply(int value) const
        {
            return scale(value);
        }
    };

    Calculator calculator;
    return calculator.apply(3);
}
