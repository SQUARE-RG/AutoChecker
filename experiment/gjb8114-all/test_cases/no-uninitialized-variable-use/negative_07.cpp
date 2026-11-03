int main()
{
    int idx;
    int arr[3] = {10, 20, 30};
    return arr[idx]; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-11-1]
}
