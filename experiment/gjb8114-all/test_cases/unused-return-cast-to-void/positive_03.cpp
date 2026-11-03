int compute(int value)
{
    return value * 2;
}

int main()
{
    int (*fn)(int) = &compute;
    (void)fn(3);
    return 0;
}
