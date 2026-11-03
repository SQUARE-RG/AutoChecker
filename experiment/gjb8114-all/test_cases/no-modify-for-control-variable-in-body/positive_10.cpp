int main()
{
    int flags = 0;
    int sum = 0;
    for (int i = 0; i < 10; i++)
    {
        flags |= (1 << i);
        sum += flags;
    }
    return sum;
}
