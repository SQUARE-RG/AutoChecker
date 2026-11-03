static int increment(int value)
{
    return value + 1;
}

static int twice_incremented(int value)
{
    return increment(value) * 2;
}

int main()
{
    int value = 3;
    int result = twice_incremented(value);
    return result == 8 ? 0 : 1;
}
