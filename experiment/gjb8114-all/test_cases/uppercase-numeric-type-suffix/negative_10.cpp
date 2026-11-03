int main()
{
    long double value = 1.0l; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-8-5]
    return static_cast<int>(value);
}
