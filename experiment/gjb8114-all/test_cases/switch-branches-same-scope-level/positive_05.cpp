int main()
{
    int x = 2;
    int z = 0;
    switch (x)
    {
    case 1:
        try
        {
            z = 1;
        }
        catch (int)
        {
            z = -1;
        }
        break;
    case 2:
        z = 2;
        break;
    default:
        z = 0;
        break;
    }
    return 0;
}
