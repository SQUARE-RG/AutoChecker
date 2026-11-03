static_assert(1LL < 2ULL, "signed long long compared with unsigned long long"); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-12-5]

int main()
{
    return 0;
}
