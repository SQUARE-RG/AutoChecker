extern int a = 2; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-19]

int main(void)
{
    a = 3;
    return 0;
}
