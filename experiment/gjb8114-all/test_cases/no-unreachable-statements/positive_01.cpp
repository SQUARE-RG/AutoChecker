int process(int para)
{
    int local = 0;
    switch (para)
    {
        case 1:
            local = para;
            break;
        case 2:
            local = para * 2;
            break;
        default:
            local = 0;
            break;
    }
    return local;
}

int main()
{
    return process(1);
}
