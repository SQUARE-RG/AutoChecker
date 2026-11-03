int main()
{
    int data[4] = {0, 0, 0, 0};
    int value = 7;
    int idx = value % 4;
    data[idx] = 1;
    return 0;
}
