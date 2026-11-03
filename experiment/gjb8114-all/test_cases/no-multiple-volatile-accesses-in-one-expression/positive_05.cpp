int main()
{
    volatile unsigned int v = 2;
    int arr[8] = {0};
    int idx = v;
    arr[idx + idx] = 7;
    return 0;
}
