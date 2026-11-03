int main()
{
    long lVar = 123456789L;
    int iVar = 0;
    iVar = lVar; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-10-2]
    return 0;
}
