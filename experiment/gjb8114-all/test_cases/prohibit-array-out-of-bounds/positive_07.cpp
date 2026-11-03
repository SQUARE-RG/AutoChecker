int main()
{
    int a[5];
    int i;
    for (i = 0; i < 5; ++i)
    {
        a[i] = i;
    }
    a[i - 1] = 0;
    return 0;
}
