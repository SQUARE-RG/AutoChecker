unsigned int fun1(void);

int main(void)
{
    return (int)fun1();
}

unsigned int fun1(void)
{
    unsigned int x = 0U;
    {
#define BLOCKDEF 2U
        x = x + BLOCKDEF;
    }
    {
#undef BLOCKDEF
    }
    return x;
}
