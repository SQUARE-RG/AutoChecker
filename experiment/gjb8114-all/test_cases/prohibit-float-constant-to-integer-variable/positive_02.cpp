int compute()
{
    int a = 7;
    int b;
    b = 12;
    return a + b;
}

int main()
{
    int result = compute();
    return result == 19 ? 0 : 1;
}
