int main(void)
{
    int a = 5;
    a %= 0; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-12]
    return a;
}
