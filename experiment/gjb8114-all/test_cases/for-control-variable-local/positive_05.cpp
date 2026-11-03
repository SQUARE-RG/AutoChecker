int sumWithParameter(int limit)
{
    int total = 0;
    for (limit = 0; limit < 10; ++limit)
    {
        total += limit;
    }
    return total;
}

int main()
{
    return sumWithParameter(0);
}
