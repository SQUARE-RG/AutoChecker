int main()
{
    auto scale = [](double factor) { return factor; };
    int input = 1;
    double result = scale(input); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-7-2]
    (void)result;
    return 0;
}
