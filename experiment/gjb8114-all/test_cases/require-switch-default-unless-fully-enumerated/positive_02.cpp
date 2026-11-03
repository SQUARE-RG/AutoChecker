int main()
{
    int i = 0;
    int j = 0;

    switch (i)
    {
        case 0:
            j = 0;
            break;
        case 1:
        case 2:
            j = 1;
            break;
        default:
            j = -1;
            break;
    }

    return j;
}
