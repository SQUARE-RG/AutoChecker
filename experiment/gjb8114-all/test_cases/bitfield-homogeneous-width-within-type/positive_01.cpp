struct ByteFlags
{
    unsigned char low : 4;
    unsigned char high : 4;
    unsigned char nextLow : 3;
    unsigned char nextHigh : 5;
};

int main()
{
    ByteFlags flags{};
    (void)flags;
    return 0;
}
