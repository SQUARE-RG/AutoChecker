int limit = 10;

int main()
{
    limit = 5;
    auto fn = [](int value) {
        int limit = value * 2;   // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-1]
        return limit;
    };
    fn(3);
    return 0;
}
