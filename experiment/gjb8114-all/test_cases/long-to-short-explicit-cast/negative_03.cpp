int main()
{
    long lValue = 100000L;
    short sBuffer[2] = {0, 0};
    sBuffer[0] = lValue; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-10-2]
    return sBuffer[0];
}
