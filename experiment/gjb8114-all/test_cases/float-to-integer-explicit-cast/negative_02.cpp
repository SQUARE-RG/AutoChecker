int main()
{
    double measurement = 3.14159;
    int rounded;
    rounded = measurement; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-10-1]
    return rounded;
}
