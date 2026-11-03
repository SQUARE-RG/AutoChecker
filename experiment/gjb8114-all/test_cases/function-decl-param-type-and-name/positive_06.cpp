void consume(int&& value);

void consume(int&& value)
{
    (void)value;
}

int main()
{
    consume(5);
    return 0;
}
