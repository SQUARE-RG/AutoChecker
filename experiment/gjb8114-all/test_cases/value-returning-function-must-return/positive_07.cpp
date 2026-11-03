int classify(int code)
{
    switch (code)
    {
        case 0:
            return 10;
        case 1:
            break;
        default:
            break;
    }
    return 20;
}

int main()
{
    return classify(2) == 20 ? 0 : 1;
}
