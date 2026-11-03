int compute(int x)
{
    do
    {
        if (x == 0)
        {
            return 1;
        }
        --x;
    } while (x > 0);
} // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-7-7]
