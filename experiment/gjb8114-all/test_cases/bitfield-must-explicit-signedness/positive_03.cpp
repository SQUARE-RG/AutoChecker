struct SignalBits
{
    signed char low : 3;
    unsigned char high : 5;
};

int main()
{
    SignalBits bits;
    bits.low = -1;
    bits.high = 3;
    return 0;
}
