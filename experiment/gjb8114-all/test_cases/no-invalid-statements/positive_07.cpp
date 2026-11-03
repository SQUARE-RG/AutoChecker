int positive_07(int a, int b)
{
    int result = (++a, b);
    return result;
}

int main()
{
    return positive_07(1, 2);
}
