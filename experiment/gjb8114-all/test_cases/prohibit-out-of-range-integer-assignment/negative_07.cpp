int main()
{
    unsigned int value = 4294967296U; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-2]
    return 0;
}
