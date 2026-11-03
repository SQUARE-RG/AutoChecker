int main()
{
    int data = 2;
    return data;
}

static auto compute(int value) noexcept -> int // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-7-13]
{
    return value * 2;
}
