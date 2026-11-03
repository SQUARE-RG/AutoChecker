int main(void)
{
    unsigned int i, tbc;
    tbc = 0x80;
    if ((tbc & 0x80) == 0x80)
    {
        i = 1;
    }
    else
    {
        i = 2;
    }
    return 0;
}
