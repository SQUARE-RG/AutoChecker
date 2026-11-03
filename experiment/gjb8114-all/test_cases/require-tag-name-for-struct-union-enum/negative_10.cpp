enum // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-8]
{
    A_Level = 0,
    B_Level,
    C_Level,
    D_Level
};

int main()
{
    return static_cast<int>(B_Level);
}
