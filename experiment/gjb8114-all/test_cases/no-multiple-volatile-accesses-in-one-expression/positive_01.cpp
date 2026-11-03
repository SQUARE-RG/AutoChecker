int main()
{
    unsigned int i, j, z[100];
    volatile unsigned int v = 1;
    for (i = 0; i < 100; ++i)
    {
        j = v;
        z[i] = 3 * j * j + 2 * j + i;
    }
    return 0;
}
