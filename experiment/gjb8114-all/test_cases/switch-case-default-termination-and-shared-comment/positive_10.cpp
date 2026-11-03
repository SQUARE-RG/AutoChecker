int sum(int selector)
{
    int total = 0;
    switch (selector)
    {
        case 1: /*shared*/
            total += 1;
            [[fallthrough]];
        case 2:
            total += 2;
            break;
        case 3:
            total += 3;
            break;
        default:
            total = -1;
            break;
    }
    return total;
}

int main()
{
    return sum(1);
}
