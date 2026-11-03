int main()
{
    int i = 0;
    double x = 0.0;

    if (0 == i)
    {
        ;
    }
    // CHECK-MESSAGES: :[[@LINE-2]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-4-2]
    else
    {
        x = 1.0;
    }

    return 0;
}
