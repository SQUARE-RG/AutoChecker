struct FlagBits
{
    int signed flag : 2;
};

int main()
{
    FlagBits bits{};
    bits.flag = -1;
    return 0;
}
