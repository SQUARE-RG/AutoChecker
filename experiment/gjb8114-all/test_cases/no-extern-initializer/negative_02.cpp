extern int arr[3] = {1, 2, 3}; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-19]

int main(void)
{
    return arr[0];
}
