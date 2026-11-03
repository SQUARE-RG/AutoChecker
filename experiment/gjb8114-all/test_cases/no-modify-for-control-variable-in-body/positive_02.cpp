int main()
{
    int sum = 0;
    int step = 1;
    for (int i = 0; i < 10; ++i)
    {
        if (i % 3 == 0)
        {
            step = 2;
        }
        sum += step;
    }
    return sum;
}
