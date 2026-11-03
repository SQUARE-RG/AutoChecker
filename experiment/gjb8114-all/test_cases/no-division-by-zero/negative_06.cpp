int main()
{
    int numerator = 42;
    int remainder = numerator % false; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-12]
    return remainder;
}
