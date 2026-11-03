int main()
{
    int x = 1;
    int *p = &x;
    *p = x;
    auto ilen = sizeof(*p);
    (void)ilen;
    return 0;
}
