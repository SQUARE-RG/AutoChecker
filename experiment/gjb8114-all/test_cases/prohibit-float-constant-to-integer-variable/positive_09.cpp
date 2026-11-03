int main()
{
    int value = 0;
    int& ref = value;
    ref = 12;
    return ref;
}
