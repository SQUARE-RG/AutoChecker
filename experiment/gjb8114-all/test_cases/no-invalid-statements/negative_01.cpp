int main()
{
    unsigned int local = 0;
    local; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-8-3]
    return 0;
}
