int main()
{
    int arr[4] = {1, 2, 3, 4};
    int idx = 0;
    unsigned long size = sizeof(arr[(idx = 1)]); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-13]
    return static_cast<int>(size);
}
