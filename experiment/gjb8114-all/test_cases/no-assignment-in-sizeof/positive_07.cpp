int main()
{
    int arr[1] = {0};
    int x = 1;
    arr[0] = x;
    auto ilen = sizeof(arr[0]);
    (void)ilen;
    return 0;
}
