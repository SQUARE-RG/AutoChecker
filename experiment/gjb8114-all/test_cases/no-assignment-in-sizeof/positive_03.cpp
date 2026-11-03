int main()
{
    int arr[4] = {1, 2, 3, 4};
    int idx = 0;
    idx = 1;
    unsigned long size = sizeof(arr[idx]);
    return static_cast<int>(size);
}
