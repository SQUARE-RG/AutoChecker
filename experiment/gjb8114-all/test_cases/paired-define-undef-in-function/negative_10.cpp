int main()
{
    auto compute = []() -> unsigned int
    {
        unsigned int x = 0U;
#define LAMBDA_DEF 3U // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-6]
        x = x + LAMBDA_DEF;
        return x;
    };

    return static_cast<int>(compute());
}
