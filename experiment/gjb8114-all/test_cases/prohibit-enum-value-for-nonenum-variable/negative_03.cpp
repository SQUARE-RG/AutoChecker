int main()
{
    enum Flags { FlagA = 1, FlagB = 2, FlagC = 4 };
    unsigned int bits = 0u;
    bits |= FlagB; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-11]
    return static_cast<int>(bits);
}
