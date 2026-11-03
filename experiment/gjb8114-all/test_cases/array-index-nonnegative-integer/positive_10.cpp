void writeWithDefault(int index = 0)
{
    int data[3] = {0, 0, 0};
    data[index] = 1;
}

int main()
{
    writeWithDefault();
    return 0;
}
