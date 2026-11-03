int classify(int v)
{
    switch (v)
    {
    case 0:
        return 0;
    case 1:
        return 1;
    default:
        return -1;
    }
}

int main()
{
    return classify(2) == -1 ? 0 : 1;
}
