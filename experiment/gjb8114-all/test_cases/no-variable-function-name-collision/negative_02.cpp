int compute_value(void)
{
    return 1;
}

int process(int compute_value) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-3]
{
    compute_value = compute_value + 1;
    return compute_value;
}
