enum ZeroEnum
{
    ZERO_VALUE = 0
};

int main()
{
    int numerator = 42;
    int quotient = numerator / ZERO_VALUE; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-12]
    return quotient;
}
