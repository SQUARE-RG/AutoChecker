int main()
{
    struct LocalFlags
    {
        signed int flag : 1; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-10]
    };

    LocalFlags flags{};
    flags.flag = -1;
    return 0;
}
