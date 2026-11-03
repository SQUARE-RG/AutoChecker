int main()
{
    int arr[1] = {0};
    int x = 1;
    auto ilen = sizeof(arr[0] = x); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-13]
    (void)ilen;
    return 0;
}
