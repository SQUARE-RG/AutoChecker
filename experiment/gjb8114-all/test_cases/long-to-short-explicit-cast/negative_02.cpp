int main()
{
    short sVar = 0;
    int iVar = 70000;
    sVar = iVar; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-10-2]
    return 0;
}
