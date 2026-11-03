int classify(int x)
{
    int value = 0;
    switch (x)
    {
        case 1:
            if (value > 0)
            {
                value = 1;
                break;
            }
            value = 2;
            break;
        case 2: /*shared*/
        case 3:
        {
            value = 3;
        }
        break;
        case 4: /*shared*/
            value = 4;
        case 5:
            value = 5;
            break;
        default:
            value = -1;
            break;
    }
    return value;
}
