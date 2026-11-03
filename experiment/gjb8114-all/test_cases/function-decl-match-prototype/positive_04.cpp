// positive_04.cpp
// Pointer parameter prototype and definition are identical.
int adjust(int* value);

int main()
{
    int n = 5;
    return adjust(&n);
}

int adjust(int* value)
{
    return *value + 1;
}
