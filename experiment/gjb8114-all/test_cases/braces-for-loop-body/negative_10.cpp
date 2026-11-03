int main()
{
    int arr[3] = {1, 2, 3};
    int sum = 0;
    for (int x : arr)
        (void)x; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-2-1]
    return sum;
}
