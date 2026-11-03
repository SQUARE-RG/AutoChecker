int main()
{
    signed char data;
    data = 128; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-2]
    return 0;
}
