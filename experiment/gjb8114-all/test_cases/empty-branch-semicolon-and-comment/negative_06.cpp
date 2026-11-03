int main()
{
    int value = 3;
    int result = 0;

    if (value == 1)
    {
        result = 10;
    }
    else if (value == 2)
    {
        result = 20;
    }
    else
    {
        ;
    } // CHECK-MESSAGES: :[[@LINE-1]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-4-2]

    return result;
}
