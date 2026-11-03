int accumulate(int selector)
{
    int total = 0;
    for (int i = 0; i < 2; ++i)
    {
        switch (selector)
        {
            case 0:
                total += 1;
                break;
            default:
                total += 2;
                break;
        }
        total += 3;
    }
    return total;
}
