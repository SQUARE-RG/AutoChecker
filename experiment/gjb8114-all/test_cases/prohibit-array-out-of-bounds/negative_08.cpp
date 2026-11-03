int main()
{
    int m[3][4] = {};
    m[2][4] = 7; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-8]
    return 0;
}
