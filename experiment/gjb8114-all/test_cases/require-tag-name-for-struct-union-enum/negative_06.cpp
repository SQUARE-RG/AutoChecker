enum : unsigned char // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-8]
{
    Level_A = 1,
    Level_B = 2
} level;

int main()
{
    level = Level_B;
    return static_cast<int>(level);
}
