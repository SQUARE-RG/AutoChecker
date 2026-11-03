int pickValue(int mode)
{
    if (mode == 0)
    {
        goto fallback;
    }
    return 42;
fallback:
    mode = 1;
} // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-7-7]
