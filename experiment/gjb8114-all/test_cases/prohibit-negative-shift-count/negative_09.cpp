int main()
{
    unsigned int value = 16u;
    value >>= static_cast<int>(-3); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-7]
    return 0;
}
