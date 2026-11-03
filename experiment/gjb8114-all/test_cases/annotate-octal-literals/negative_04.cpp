int main()
{
    int flags = 0;
    flags |= 020; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-8-4]
    return flags;
}
