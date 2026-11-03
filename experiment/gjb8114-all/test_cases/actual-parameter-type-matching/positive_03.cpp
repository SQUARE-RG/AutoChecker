long multiply(long factor);

int main()
{
    long value = 5;
    return static_cast<int>(multiply(value));
}

long multiply(long factor)
{
    return factor * 2;
}
