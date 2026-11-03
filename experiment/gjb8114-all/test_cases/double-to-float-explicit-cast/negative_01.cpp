int main(void)
{
    double dData = 0.0;
    float fData;
    fData = dData; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-10-3]
    return 0;
}
