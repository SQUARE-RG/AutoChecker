struct PacketFlags
{
    char kind : 4; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-11]
    signed char level : 4;
};

int main()
{
    PacketFlags flags;
    flags.kind = 1;
    flags.level = -1;
    return 0;
}
