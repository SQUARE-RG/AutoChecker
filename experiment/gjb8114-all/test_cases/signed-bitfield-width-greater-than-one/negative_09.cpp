struct FlagBits
{
    int signed flag : 1; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-10]
};

int main()
{
    FlagBits bits{};
    bits.flag = -1;
    return 0;
}
