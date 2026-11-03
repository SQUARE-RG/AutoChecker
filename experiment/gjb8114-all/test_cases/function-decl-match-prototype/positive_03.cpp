// positive_03.cpp
// Multi-parameter prototype and definition are identical.
int multiply(int x, int y);

int main()
{
    int a = 3;
    int b = 4;
    return multiply(a, b);
}

int multiply(int x, int y)
{
    return x * y;
}
