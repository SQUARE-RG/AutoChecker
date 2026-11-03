int main()
{
    int total = 0;
    for (int i = 0; i < 10; ++i) if (i % 2 == 0) { total += i; } // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-2-1]
    return total;
}
