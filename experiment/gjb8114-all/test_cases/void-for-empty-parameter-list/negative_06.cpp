auto compute() -> int // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-23]
{
    return 0;
}

int main(void)
{
    return compute();
}
