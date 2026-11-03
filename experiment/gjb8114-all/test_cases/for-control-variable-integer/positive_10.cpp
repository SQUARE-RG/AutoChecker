int main()
{
    long total = 0;
    for (long i = 64; i > 0; i /= 2)
    {
        total += i;
    }
    return 0;
}
