int main()
{
    unsigned int i, z[100];
    volatile unsigned int v = 1;
    for (i = 0; i < 100; ++i)
    {
        z[i] = 3 * v * v + 2 * v + i; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-13]
    }
    return 0;
}
