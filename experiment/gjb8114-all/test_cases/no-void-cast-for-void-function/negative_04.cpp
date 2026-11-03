int main()
{
    auto f = [](int value) {
        if (value < 0) {
            value = -value;
        }
    };
    (void)f(7); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-7-12]
    return 0;
}
