int main()
{
    double d = 3.14159;
    unsigned long long ull = d; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-10-1]
    (void)ull;
    return 0;
}
