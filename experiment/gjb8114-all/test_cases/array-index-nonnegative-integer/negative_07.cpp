int main()
{
    int data[4] = {0, 0, 0, 0};
    data[~0] = 1; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-9]
    return 0;
}
