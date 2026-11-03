int main()
{
    unsigned int a = 0x00u;
    unsigned int b = 0x01u;
    unsigned int c = 0x20u;
    while (a ^ b <= c) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-2-5]
    {
        ++a;
    }
    return 0;
}
