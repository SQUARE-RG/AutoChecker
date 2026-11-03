int main()
{
    volatile unsigned int v = 2;
    unsigned int result = (v << 1) | (v >> 1); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-13]
    (void)result;
    return 0;
}
