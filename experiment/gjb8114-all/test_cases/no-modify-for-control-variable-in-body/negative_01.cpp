int main()
{
    int k = 0;
    for (int i = 0; i < 10; i++)
    {
        i = 2 * i; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-9-3]
        k = k + 1;
    }
    return k;
}
