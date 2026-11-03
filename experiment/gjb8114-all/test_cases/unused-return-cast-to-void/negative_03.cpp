int compute(int value)
{
    return value * 2;
}

int main()
{
    int (*fn)(int) = &compute;
    fn(3); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-7-11]
    return 0;
}
