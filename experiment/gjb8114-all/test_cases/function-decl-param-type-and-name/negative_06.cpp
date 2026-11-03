int compute(int = 42); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-13]

int compute(int value)
{
    return value;
}

int main()
{
    int result = compute();
    return result == 42 ? 0 : 1;
}
