int main()
{
    int values[] = {1, 2, 3};
    for (int value : values)
    {
        if (value == 2)
        {
            return 0;
        }
    }
    return 1;
}
