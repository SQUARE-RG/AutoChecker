int twice(int p)
{
    return 2 * p;
}

int main()
{
    int x = 1;
    int y = 2;
    if (x < y) {
        x++;
    }
    int r = twice(5);
    return r;
}
