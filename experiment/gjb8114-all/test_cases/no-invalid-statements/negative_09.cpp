int main(void)
{
    int value = 0;
    sizeof(value); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-8-3]
    return (0);
}
