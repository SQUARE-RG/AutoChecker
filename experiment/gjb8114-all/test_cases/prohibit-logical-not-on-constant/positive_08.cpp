bool isZero(int input)
{
    const int value = input + 0;
    return !value;
}

int main()
{
    int x = 0;
    return isZero(x) ? 0 : 1;
}
