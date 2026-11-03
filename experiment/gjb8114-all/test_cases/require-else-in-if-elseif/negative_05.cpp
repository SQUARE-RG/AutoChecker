int main()
{
    int sum = 0;
    for (int i = 0; i < 4; ++i)
    {
        if (i == 0) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-4-1]
        {
            sum += 1;
        }
        else if (i == 1)
        {
            sum += 2;
        }
    }
    return sum;
}
