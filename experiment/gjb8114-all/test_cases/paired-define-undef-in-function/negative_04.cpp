#define GLOBAL_MACRO 2U

unsigned int fun2(void);

int main(void)
{
    return (int)fun2();
}

unsigned int fun2(void)
{
    unsigned int x = 0U;
    x = x + GLOBAL_MACRO;
#undef GLOBAL_MACRO // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-6]
    return x;
}
