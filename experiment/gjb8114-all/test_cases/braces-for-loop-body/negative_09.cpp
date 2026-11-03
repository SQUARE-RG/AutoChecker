int main()
{
    int sum = 0;
    for (int i = 0; i < 10; ++i)
        ++sum; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-2-1]
    return sum;
}
