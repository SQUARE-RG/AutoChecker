int main()
{
    int value = 2147483648; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-2]
    (void)value;
    return 0;
}
