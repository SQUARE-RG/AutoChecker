int main()
{
    if (int arr[]{1, 2, 3}; arr[0] == 1) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-18]
    {
        return arr[2] - 3;
    }
    return 1;
}
