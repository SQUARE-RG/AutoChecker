int main(void)
{
    int limit = 10;
    int total = 0;
    for (int i = 0; i < limit; ++i)
    {
        int limit = i * 2; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-7]
        total += limit;
    }
    return total;
}
