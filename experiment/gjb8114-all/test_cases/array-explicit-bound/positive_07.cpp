int main()
{
    static int values[3] = {1, 2, 3};
    int sum = 0;
    for (int i = 0; i < 3; ++i)
    {
        sum += values[i];
    }
    return sum;
}
