int main()
{
    constexpr bool negative_shift = true;
    unsigned int value = 1u;
    value = value << (negative_shift ? -2 : 1); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-7]
    return 0;
}
