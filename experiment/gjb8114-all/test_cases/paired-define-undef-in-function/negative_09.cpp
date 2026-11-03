auto fun1() -> unsigned int
{
    unsigned int x = 0U;
#define BLOCKDEF 2U // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-6]
    x = x + BLOCKDEF;
    return x;
}

int main()
{
    return static_cast<int>(fun1());
}
