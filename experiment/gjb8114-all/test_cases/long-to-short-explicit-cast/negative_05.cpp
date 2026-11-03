int main()
{
    long long wideValue = 0LL;
    signed char narrowValue = 0;
    narrowValue = wideValue; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-10-2]
    return 0;
}
