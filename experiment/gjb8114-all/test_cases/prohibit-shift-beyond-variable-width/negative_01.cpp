int main()
{
    unsigned int x = 0x00000001u;
    unsigned int y = x << 33; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-6]
    (void)y;
    return 0;
}
