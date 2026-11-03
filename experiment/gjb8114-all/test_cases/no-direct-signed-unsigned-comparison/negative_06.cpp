bool is_ge(long long signed_value, unsigned long long unsigned_value)
{
    return signed_value >= unsigned_value; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-12-5]
}

int main()
{
    return is_ge(-1LL, 1ULL) ? 0 : 1;
}
