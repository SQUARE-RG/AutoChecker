int main()
{
    for (int i = 0; i < 5; ++i)
    {
        if (i == 2)
        {
            --i; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-9-3]
            break;
        }
    }
    return 0;
}
