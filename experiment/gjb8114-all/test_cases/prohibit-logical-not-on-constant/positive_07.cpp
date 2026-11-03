bool isZero(int value)
{
    return !(value + 0);
}

int main()
{
    int x = 5;
    bool result = isZero(x);
    return result ? 0 : 1;
}
