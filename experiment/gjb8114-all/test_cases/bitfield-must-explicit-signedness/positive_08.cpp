union Bits
{
    signed short value : 4;
    unsigned int whole : 8;
};

int main()
{
    Bits b{};
    b.value = 1;
    b.whole = 0;
    return 0;
}
