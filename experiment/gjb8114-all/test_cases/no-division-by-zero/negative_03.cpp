int main()
{
    int a = 5;
    int c;
    c = a / 0; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-12]
    (void)c;
    return 0;
}
