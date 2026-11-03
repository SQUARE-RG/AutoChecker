int classify(int x)
{
    switch (x)
    {
        case 1:
            return 1;
        case 2: /*shared*/
        case 3:
            return 2;
        case 4: /*shared*/
        case 5:
            return 3;
        default:
            return -1;
    }
}
