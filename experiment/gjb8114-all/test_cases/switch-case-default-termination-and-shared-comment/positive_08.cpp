int compute(int x)
{
    switch (x)
    {
        case 1: /*shared*/
        case 2:
            return 10;
        case 3:
            break;
    }
    return 0;
}

int main()
{
    return compute(3);
}
