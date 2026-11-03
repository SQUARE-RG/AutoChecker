int main(void)
{
    int Data[3] = {0, 0, 0};
    int i = 2;
    Data[-i] = 1; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-9]
    return 0;
}
