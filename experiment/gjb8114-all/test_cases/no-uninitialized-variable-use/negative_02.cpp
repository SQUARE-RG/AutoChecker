int main()
{
    double base = 2.0;
    double offset;
    double result = base + offset; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-11-1]
    return 0;
}
