int main()
{
    int a = 0;
    if (a == 0)
    {
        a = 1;
    }
    else if (a == 1)
    {
        ; /* nothing to do */ // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-4-2]
    }
    else
    {
        a = 2;
    }
    return 0;
}
