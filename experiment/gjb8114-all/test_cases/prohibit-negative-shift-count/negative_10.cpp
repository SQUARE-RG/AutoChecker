int main()
{
    unsigned int value = 1u;
    int shift = -4;
    value <<= shift; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-7]
    return 0;
}
