static int initial_value()
{
    return 3;
}

int main()
{
    static int value = initial_value();
    return value;
}
