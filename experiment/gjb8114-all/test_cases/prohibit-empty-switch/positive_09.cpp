int main()
{
    int value = 1;
    try
    {
        switch (value)
        {
        case 0:
            throw 0;
        default:
            break;
        }
    }
    catch (int)
    {
        return 0;
    }
    return 1;
}
