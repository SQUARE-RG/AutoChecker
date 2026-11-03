void helper()
{
}

int main()
{
    auto run = []() {
        int helper = 0; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-3]
        return helper;
    };
    return run();
}
