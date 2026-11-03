int main()
{
    long long value;
    value = 18446744073709551615ULL; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-2]
    return 0;
}
