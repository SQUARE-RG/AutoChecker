int main()
{
    unsigned short data = 65536; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-2]
    return 0;
}
