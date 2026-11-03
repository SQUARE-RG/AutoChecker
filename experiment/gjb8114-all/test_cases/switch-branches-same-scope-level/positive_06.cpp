int main()
{
    int x = 2;
    int z = 0;
    switch (x)
    {
    case 1:
        for (int i = 0; i < 3; ++i)
        {
            z += i;
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
