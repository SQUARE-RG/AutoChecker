int main()
{
    int sum = 0;
    for (int i = 0; i < 100; i++)
    {
        i |= 1; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-9-3]
        sum += i;
    }
    return sum;
}
