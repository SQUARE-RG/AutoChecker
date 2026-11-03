int main()
{
    int total = 0;
    for (int i = 0, j = 10; i < 5; ++i, --j)
    {
        total += i + j;
    }
    return total;
}
