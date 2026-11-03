int main()
{
    int a = 5;
    int b = 0;
    int d;
    d = a % b; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-12]
    (void)d;
    return 0;
}
