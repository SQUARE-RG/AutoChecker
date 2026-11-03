int main()
{
    short value = 32768; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-2]
    (void)value;
    return 0;
}
