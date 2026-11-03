int main()
{
    unsigned int value = 5u;
    return value >= 0; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-12-4]
}
