int compute(int value)
{
    return value + 2;
}

int main()
{
    int local = 1;
    (compute(local), 0); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-7-11]
    return 0;
}
