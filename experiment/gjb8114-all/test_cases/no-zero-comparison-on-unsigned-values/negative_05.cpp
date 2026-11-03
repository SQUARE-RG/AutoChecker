int main()
{
    unsigned int n = 0u;
    int count = 0;
    while (n <= 0u) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-12-4]
    {
        ++count;
        ++n;
    }
    return count;
}
