int compute(int x)
{
    switch (x)
    {
        case 0:
            return 0;
        case 1: /*shared*/
        case 2:
            return 10;
        case 3:
            break;
        default:
            break;
    }
    return -1;
}

int main()
{
    return compute(0);
}
