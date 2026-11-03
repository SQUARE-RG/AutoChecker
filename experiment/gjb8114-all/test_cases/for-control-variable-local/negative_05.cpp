int counters[1] = {0};

int main()
{
    int sum = 0;
    for (counters[0] = 0; counters[0] < 10; ++counters[0]) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-9-1]
    {
        sum += counters[0];
    }
    return sum;
}
