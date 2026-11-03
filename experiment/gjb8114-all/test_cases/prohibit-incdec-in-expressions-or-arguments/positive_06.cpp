int triple(int p)
{
    return 3 * p;
}

int main()
{
    int a = 3;
    int b = 4;
    while (a < b) {
        a++;
    }
    b--;
    int r = triple(a + b);
    return r;
}
