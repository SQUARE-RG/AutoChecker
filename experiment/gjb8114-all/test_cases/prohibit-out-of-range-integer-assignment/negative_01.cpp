int main()
{
    unsigned char data = 256; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-2]
    (void)data;
    return 0;
}
