int main()
{
    unsigned int ydata = 32;
    int shift = (ydata > 0) ? 2 : 1;
    ydata >>= shift;
    return 0;
}
