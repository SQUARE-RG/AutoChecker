int main()
{
    int idata = 0;
    idata = 6.25; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-1]
    return idata;
}
