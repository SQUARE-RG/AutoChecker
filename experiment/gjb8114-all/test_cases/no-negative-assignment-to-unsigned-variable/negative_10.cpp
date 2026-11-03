int main()
{
    unsigned char value = 0;
    value = -1; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-15]
    return 0;
}
