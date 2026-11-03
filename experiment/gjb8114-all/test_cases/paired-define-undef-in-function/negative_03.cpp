unsigned int fun1(void);

int main(void)
{
    return (int)fun1();
}

unsigned int fun1(void)
{
    unsigned int x = 0U;
#define BLOCKDEF 2U // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-6]
    x = x + BLOCKDEF;
    return x;
}

#undef BLOCKDEF
