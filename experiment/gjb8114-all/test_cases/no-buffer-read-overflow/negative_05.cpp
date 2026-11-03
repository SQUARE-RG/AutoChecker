int main()
{
    int src[2] = {1, 2};
    int value = src[2]; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-14]
    (void)value;
    return 0;
}
