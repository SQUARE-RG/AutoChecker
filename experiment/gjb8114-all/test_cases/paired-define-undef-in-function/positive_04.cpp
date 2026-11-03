unsigned int fun1(void);

int main(void)
{
    return (int)fun1();
}

unsigned int fun1(void)
{
    unsigned int x = 0U;
#if 1
#define BLOCKDEF 3U
#endif
    x = x + BLOCKDEF;
#if 1
#undef BLOCKDEF
#endif
    return x;
}
