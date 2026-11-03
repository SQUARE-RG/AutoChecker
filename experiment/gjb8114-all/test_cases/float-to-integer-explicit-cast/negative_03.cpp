int main()
{
    long double source = 8.125L;
    unsigned int target;
    target = source; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-10-1]
    return 0;
}
