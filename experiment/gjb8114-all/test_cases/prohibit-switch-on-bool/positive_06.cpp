int main()
{
    int x = 3;
    int y = 0;
    switch (x & 1)
    {
        case 0:
            y = 1;
            break;
        case 1:
            y = 2;
            break;
    }
    return y;
}
