int main()
{
    int total = 0;
    for (int i = 0; i < 10; ++i)
    {
        ++i; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-9-3]
        total += i;
    }
    return total;
}
