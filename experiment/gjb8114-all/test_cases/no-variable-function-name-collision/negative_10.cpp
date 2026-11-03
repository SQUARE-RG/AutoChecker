int next_value()
{
    return 1;
}

int main()
{
    while (int next_value = 0) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-3]
    {
        (void)next_value;
    }
    return 0;
}
