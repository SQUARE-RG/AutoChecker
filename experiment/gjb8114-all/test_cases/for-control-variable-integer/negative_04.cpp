int main()
{
    long double total = 0.0L;
    for (long double x = 5.0L; x > 0.0L; x -= 0.5L) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-9-2]
    {
        total += x;
    }
    return static_cast<int>(total);
}
