int selectValue(int value)
{
    int result = 0;
    switch (value)
    {
        case 0:
            result = 100;
            break;
        default:
            result = -1;
            break;
        case 2:
            result = value;
            break;
    }
    return result;
}
