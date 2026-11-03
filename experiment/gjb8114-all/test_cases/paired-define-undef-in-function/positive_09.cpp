auto fun2() -> unsigned int
{
    unsigned int x = 0U;
#define BLOCKDEF 2U
    x = x + BLOCKDEF;
#undef BLOCKDEF
    return x;
}

int main()
{
    return static_cast<int>(fun2());
}
