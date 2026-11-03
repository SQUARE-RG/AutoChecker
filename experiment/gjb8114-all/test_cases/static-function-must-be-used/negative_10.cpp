[[nodiscard]] static int compute(int value) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-7-13]
{
    return value * 2;
}

int main()
{
    return 0;
}
