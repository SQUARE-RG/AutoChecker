int main()
{
    unsigned int flags = 0x81;
    for (int i = 0; flags & 0x01 == 0x01; ++i) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-2-5]
    {
        break;
    }
    return 0;
}
