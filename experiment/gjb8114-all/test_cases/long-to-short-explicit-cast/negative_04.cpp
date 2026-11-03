int main()
{
    long lValue = 42L;
    short sValue = 0;
    short* pShort = &sValue;
    *pShort = lValue; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-10-2]
    return *pShort;
}
