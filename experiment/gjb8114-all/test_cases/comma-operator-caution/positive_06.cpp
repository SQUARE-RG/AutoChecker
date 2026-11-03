int combine(int x, int y)
{
    return x + y;
}
int main()
{
    int a = 1;
    int b = 2;
    int result = combine(a, b);
    return result == 3 ? 0 : 1;
}
