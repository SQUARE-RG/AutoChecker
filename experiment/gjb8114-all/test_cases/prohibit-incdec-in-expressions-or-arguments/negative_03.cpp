int compute(int value)
{
    return value + 1;
}

int main()
{
    int x = 10;
    int result = compute(x--); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-5]
    return result;
}
