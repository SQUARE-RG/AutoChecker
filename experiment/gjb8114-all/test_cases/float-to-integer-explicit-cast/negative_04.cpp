int main()
{
    double source = 12.5;
    short target;
    target = source; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-10-1]
    return 0;
}
