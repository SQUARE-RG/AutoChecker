int main()
{
    int x = 2;
    int z = 0;

    switch (x)
    {
        case 1:
            if constexpr (sizeof(int) == 4)
            {
                z = 1;
            }
            else
            {
                z = 2;
            }
            break;
        case 2:
            z = 3;
            break;
        default:
            z = 4;
            break;
    }

    return z;
}
