int main()
{
    volatile unsigned int v = 2;
    unsigned int tmp = v;
    unsigned int result = (tmp << 1) | (tmp >> 1);
    (void)result;
    return 0;
}
