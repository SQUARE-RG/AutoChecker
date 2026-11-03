int main()
{
    long lValue = 100000L;
    short sBuffer[2] = {0, 0};
    sBuffer[0] = static_cast<short>(lValue);
    return sBuffer[0];
}
