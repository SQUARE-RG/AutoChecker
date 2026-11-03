long sum(long a, int b);

int main()
{
    return 0;
}

long sum(long a, long b) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-7-5]
{
    return a + b;
}
