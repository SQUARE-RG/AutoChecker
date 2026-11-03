int main()
{
    unsigned int flags = 0x81;
    for (int i = 0; (flags & 0x01) == 0x01; ++i)
    {
        break;
    }
    return 0;
}
