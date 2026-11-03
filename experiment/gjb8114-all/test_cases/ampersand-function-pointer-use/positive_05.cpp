using BinaryOp = int (*)(int, int);

int subtract(int a, int b)
{
    return a - b;
}

BinaryOp get_operation()
{
    return &subtract;
}

int main()
{
    BinaryOp op = get_operation();
    return op(10, 3);
}
