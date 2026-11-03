int main()
{
    unsigned int state = 0x10u;
    unsigned int kFlag = 0x01u;
    unsigned int threshold = 0x20u;
    if (state | kFlag < threshold) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-2-5]
    {
        state = 0u;
    }
    return 0;
}
