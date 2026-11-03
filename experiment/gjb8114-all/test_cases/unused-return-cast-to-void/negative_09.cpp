int compute(int value)
{
    return value + 1;
}

int main()
{
    for (int i = 0; i < 3; compute(i)) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-7-11]
    {
        ++i;
    }
    return 0;
}
