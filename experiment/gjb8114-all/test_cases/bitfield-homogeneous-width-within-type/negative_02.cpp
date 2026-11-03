struct WideFlags
{
    unsigned short a : 2;
    unsigned short b : 2;
    unsigned short c : 2;
    unsigned short d : 12; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-12]
    unsigned short e : 2;
};

int main()
{
    WideFlags flags{};
    (void)flags;
    return 0;
}
