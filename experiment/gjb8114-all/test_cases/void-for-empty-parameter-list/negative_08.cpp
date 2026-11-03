constexpr int compute() // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-23]
{
    return 42;
}

int main(void)
{
    return compute();
}
