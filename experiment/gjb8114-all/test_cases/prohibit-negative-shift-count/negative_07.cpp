int main()
{
    constexpr int shift = 3;
    unsigned int value = 16u;
    value >>= -shift; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-7]
    return 0;
}
