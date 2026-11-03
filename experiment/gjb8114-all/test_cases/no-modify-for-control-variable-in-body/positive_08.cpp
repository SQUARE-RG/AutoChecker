int main()
{
    int mask = 0;
    int limit = 5;
    for (int i = 0; i < limit; ++i)
    {
        mask ^= 1;
    }
    return mask;
}
