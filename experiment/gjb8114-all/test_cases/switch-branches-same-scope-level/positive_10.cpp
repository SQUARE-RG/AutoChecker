int main()
{
    int x = 2;
    int z = 0;
    switch (x)
    {
        case 1:
            goto end;
        case 2:
            z = 1;
            break;
        default:
            z = 2;
            break;
    }
end:
    return 0;
}
