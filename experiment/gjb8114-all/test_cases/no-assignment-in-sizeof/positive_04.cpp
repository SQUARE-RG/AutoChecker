int identity(int value)
{
    return value;
}

int main()
{
    int x = 0;
    x = 5;
    unsigned long size = sizeof(identity(x));
    return static_cast<int>(size);
}
