int main()
{
    int idata = 2.5; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-1]
    idata = idata + 1;
    return 0;
}
