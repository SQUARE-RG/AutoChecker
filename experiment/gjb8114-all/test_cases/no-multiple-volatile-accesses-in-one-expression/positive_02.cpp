int main()
{
    volatile int v = 5;
    int a = v;
    int b = v + 1;
    int c = a + b + v;
    return a + b + c;
}
