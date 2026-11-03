int main()
{
    int i = 0;
    int j = 0;
    if (i == 0)
    {
        j = 1;
    }
    else if (i == 1)
        j = 3; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-2-2]
    else
    {
        j = 5;
    }
    return 0;
}
