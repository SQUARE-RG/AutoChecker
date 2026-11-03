void func(int para)
{
    para = para + 1;
}

int main()
{
    void (*fn)(int) = &func;
    fn(7);
    return 0;
}
