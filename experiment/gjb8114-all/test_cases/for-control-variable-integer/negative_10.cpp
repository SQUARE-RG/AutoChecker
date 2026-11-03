int main()
{
    double d = 0.0;
    double total = 0.0;
    for (d = 1.0; d != 9.0; d += 1.0) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-9-2]
    {
        total += d;
    }
    return 0;
}
