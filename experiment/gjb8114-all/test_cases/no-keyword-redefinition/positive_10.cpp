int classify(int value)
{
    int result = 0;
    switch (value)
    {
    case 0:
        result = 10;
        break;
    case 1:
        result = 20;
        break;
    default:
        result = 30;
        break;
    }
    return result;
}

int main()
{
    return classify(1);
}
