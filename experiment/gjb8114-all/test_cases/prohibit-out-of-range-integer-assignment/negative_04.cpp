int main()
{
    short data;
    data = -32769; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-2]
    return 0;
}
