int compute(); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-23]

int compute(void)
{
    return 21;
}

int main(void)
{
    return compute();
}
