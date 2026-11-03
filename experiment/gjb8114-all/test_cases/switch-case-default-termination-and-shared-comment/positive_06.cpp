int select(int outer, int inner)
{
    int value = 0;
    switch (outer)
    {
        case 1:
            switch (inner)
            {
                case 1:
                    value = 10;
                    break;
                case 2:
                    value = 20;
                    break;
                default:
                    value = 30;
                    break;
            }
            break;
        case 2:
            value = 40;
            break;
        default:
            value = -1;
            break;
    }
    return value;
}

int main()
{
    return select(1, 1);
}
