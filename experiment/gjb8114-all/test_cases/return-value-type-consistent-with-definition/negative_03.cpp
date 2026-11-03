long long scale(long long value)
{
    double converted = static_cast<double>(value) * 1.5;
    return converted; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-7-10]
}

int main()
{
    long long result = scale(3);
    (void)result;
    return 0;
}
