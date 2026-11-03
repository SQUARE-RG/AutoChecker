int main()
{
    double total = 0.0;
    for (double step = 0.0; step < 5.0; step += 1.0) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-9-2]
    {
        total += step;
    }
    return 0;
}
