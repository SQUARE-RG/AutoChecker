int main()
{
    int a[5];
    int i;
    for (i = 0; i < 5; ++i)
    {
        a[i] = i;
    }
    a[i] = 0; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-8]
    return 0;
}
