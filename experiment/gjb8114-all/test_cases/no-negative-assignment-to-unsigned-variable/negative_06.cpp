int main()
{
    bool flag = true;
    unsigned long value = flag ? -7 : 7; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-15]
    return 0;
}
