int adjust(long value);

int adjust(long long value) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-7-5]
{
    return static_cast<int>(value);
}

int main()
{
    return 0;
}
