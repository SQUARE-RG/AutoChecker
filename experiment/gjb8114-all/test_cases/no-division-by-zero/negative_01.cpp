int main(void)
{
    int a = 5;
    int b = 0;
    int c = a / b; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-12]
    return c;
}
