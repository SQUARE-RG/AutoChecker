int compute(int value)
{
    return value * 2;
}

void consume(int value)
{
    (void)value;
}

int main()
{
    consume(compute(3));
    return 0;
}
