int main()
{
    int limit = 5;
    for (int i = 0; i < limit; ++i)
    {
        i ^= 1; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-9-3]
    }
    return 0;
}
