int compute(int value)
{
    return value + 3;
}

int main()
{
    int x = 5;
    int y = 7;
    x++;
    y--;
    int result = compute(x + y);
    return result;
}
