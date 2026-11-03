typedef enum // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-8]
{
    A_Level = 0,
    B_Level,
    C_Level,
    D_Level
} ELevel;

int main()
{
    ELevel level = B_Level;
    return static_cast<int>(level);
}
