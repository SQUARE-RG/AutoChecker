int main()
{
    int value = 0;
    int* ptr = &value;
    bool b = !*ptr;
    return b ? 0 : 1;
}
