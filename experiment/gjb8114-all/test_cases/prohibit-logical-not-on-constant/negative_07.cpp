int main()
{
    int count = 0;
    while (!0u) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-10]
    {
        ++count;
        if (count > 1)
        {
            break;
        }
    }
    return 0;
}
