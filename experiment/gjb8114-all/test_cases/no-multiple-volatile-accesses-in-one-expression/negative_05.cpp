int main()
{
    volatile unsigned int v = 2;
    int arr[8] = {0};
    arr[v + v] = 7; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-13]
    return 0;
}
