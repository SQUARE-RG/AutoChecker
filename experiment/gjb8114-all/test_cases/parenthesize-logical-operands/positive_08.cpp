int main()
{
    unsigned int a = 0x00u;
    unsigned int b = 0x01u;
    unsigned int c = 0x20u;
    while ((a ^ b) <= c)
    {
        ++a;
    }
    return 0;
}
