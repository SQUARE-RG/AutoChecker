int scale(int& value);

int scale(int& value)
{
    return value * 2;
}

int main()
{
    int input = 21;
    return scale(input) == 42 ? 0 : 1;
}
