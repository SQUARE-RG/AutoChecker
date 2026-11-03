int mapValue(int code)
{
    int value = 0;
    switch (code)
    {
        case 1: /*shared*/ case 2:
            value = 10;
            break;
        case 3:
            value = 20;
            break;
        default:
            value = -1;
            break;
    }
    return value;
}

int main()
{
    return mapValue(1);
}
