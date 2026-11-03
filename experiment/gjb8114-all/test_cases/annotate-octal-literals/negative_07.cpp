int main()
{
    int value = 0;
    value = 010;
    // CHECK-MESSAGES: :[[@LINE-1]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-8-4]
    return value;
}
