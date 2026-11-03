int main()
{
    int a = 10;
    int b = a / (1 - 1); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-12]
    return b;
}
