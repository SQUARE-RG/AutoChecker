int process(int value)
{
    for (int i = 0; i < 4; ++i)
    {
        switch (value) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-4-5]
            default:
                continue;
        }
    }
    return value;
}
