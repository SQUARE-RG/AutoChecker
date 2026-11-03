int main()
{
    signed char data = -129; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-2]
    (void)data;
    return 0;
}
