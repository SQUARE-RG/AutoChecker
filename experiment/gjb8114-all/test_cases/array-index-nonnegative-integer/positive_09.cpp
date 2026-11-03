int nonNegativeIndex()
{
    return 1;
}

int main()
{
    int data[3] = {0, 0, 0};
    data[nonNegativeIndex()] = 1;
    return 0;
}
