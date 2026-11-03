int main()
{
    volatile unsigned int v = 1;
    unsigned int t = v;
    switch (t + t)
    {
    case 2:
        return 0;
    default:
        break;
    }
    return 1;
}
