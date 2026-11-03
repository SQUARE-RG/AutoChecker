using BinaryOp = int (*)(int, int);

int subtract(int a, int b)
{
    return a - b;
}

BinaryOp get_operation()
{
    return subtract; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-3-2]
}

int main()
{
    BinaryOp op = get_operation();
    return op(10, 3);
}
