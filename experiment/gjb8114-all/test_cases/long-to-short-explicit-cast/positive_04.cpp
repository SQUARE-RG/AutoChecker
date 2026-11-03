int main()
{
    long lValue = 42L;
    short sValue = 0;
    short* pShort = &sValue;
    *pShort = static_cast<short>(lValue);
    return *pShort;
}
