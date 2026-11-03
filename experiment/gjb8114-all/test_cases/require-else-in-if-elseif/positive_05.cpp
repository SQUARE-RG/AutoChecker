int main()
{
    int sum = 0;
    for (int i = 0; i < 4; ++i)
    {
        if (i == 0)
        {
            sum += 1;
        }
        else if (i == 1)
        {
            sum += 2;
        }
        else
        {
            sum += 3;
        }
    }
    return sum;
}
