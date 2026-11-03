int main()
{
    long long product = 1;
    for (long long i = 1; i <= 5; i += 2)
    {
        product *= i;
    }
    return product > 0 ? 0 : 1;
}
