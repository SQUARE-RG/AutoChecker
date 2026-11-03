int compute(int value)
{
    return value + 1;
    value += 1; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-8-1]
}

int main()
{
    return compute(3);
}
