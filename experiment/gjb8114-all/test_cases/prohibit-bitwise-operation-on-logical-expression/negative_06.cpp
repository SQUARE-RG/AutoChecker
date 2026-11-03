int main()
{
    static_assert((sizeof(int) >= 1) & (sizeof(long) >= 1), "type sizes must be positive"); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-4]
    return 0;
}
