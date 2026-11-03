auto multiply(int a, int b) -> int;

auto multiply(int a, int b) -> int
{
    return a * b;
}

int main()
{
    int result = multiply(6, 7);
    return result == 42 ? 0 : 1;
}
