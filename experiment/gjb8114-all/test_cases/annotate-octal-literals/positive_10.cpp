int main()
{
    int values[10] = {0};
    int* ptr = values;
    ptr = ptr + 010 /* octal */;
    return *ptr;
}
