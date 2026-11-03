int main()
{
    unsigned int mask = 0xF0u;
    mask >>= ~1; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-7]
    return static_cast<int>(mask);
}
