int classify(int value)
{
    if (value == 3 || value == 4)
    {
        return 1;
    }
    else
    {
        return 0;
    }
}

int main()
{
    return classify(5);
}
