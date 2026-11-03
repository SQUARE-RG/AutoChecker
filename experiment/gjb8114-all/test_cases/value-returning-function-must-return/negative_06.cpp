int handle(int x)
{
    try
    {
        if (x > 0)
        {
            return x;
        }
    }
    catch (...)
    {
        return -1;
    }
} // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-7-7]
