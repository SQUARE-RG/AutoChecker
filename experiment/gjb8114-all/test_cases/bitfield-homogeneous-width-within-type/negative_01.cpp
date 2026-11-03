struct MixedFlags
{
    unsigned char low : 4;
    unsigned char high : 4;
    unsigned short wide : 4; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-12]
};

int main()
{
    MixedFlags flags{};
    (void)flags;
    return 0;
}
