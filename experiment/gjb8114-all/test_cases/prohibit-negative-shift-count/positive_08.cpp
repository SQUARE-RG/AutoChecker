int main()
{
    constexpr unsigned int shifts[] = {0u, 2u, 4u};
    unsigned int value = 64u;
    value >>= shifts[1];
    return 0;
}
