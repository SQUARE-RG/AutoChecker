int increment(char value) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-20]
{
    return value + 1;
}

int main()
{
    int result = increment(41);
    return result - 42;
}
