int comp(int data1, int data2);

int main()
{
    int v = 10;
    int d = 20;
    int h = comp(v, d);
    return 0;
}

int comp(int data1, int data2)
{
    return 2 * data1 + data2;
}
