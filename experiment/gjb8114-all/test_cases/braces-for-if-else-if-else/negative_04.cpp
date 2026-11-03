int main()
{
    int x = 0;
    int y = 0;
    if (x == 0)
    {
        y = 1;
    }
    else
    {
        if (x == 1)
            y = 2; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-2-2]
    }
    return y;
}
