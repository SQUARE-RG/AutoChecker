int main()
{
    static int values[] = {1, 2, 3}; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-18]
    int sum = 0;
    for (int i = 0; i < 3; ++i)
    {
        sum += values[i];
    }
    return sum;
}
