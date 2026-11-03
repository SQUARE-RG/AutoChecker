struct PacketFlags
{
    int mode : 4; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-11]
    unsigned int reserved : 4;
};

int main()
{
    PacketFlags flags{};
    flags.mode = 3;
    flags.reserved = 0;
    return flags.mode;
}
