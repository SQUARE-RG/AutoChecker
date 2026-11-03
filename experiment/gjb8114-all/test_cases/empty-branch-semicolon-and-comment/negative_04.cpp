int main()
{
    int a = 0;
    if (a == 0)
    {
        /* no deal with */ // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-4-2]
    }
    return 0;
}
