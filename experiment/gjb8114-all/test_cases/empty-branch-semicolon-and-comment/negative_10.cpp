int main()
{
    int mode = 2;
    int result = 0;

    if (mode == 0)
    {
        result = 10;
    }
    else if (mode == 1)
    {
        result = 20;
    }
    else if (mode == 2)
    {
        ; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-4-2]
    }
    else
    {
        result = 30;
    }

    return result;
}
