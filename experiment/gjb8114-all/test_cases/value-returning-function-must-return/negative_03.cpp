int accumulate(int value)
{
    while (value > 0)
    {
        if (value == 3)
        {
            return value * 10;
        }
        value--;
    }
} // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-7-7]
