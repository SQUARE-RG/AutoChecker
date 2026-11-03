static int multiply_by_two(int value)
{
    return value * 2;
}

int main()
{
    int (*operation)(int) = &multiply_by_two;
    return operation(21) == 42 ? 0 : 1;
}
