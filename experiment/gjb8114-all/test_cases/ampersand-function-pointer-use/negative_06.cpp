using BinaryOp = int (*)(int, int);

int add(int a, int b)
{
    return a + b;
}

int subtract(int a, int b)
{
    return a - b;
}

BinaryOp choose(bool use_add)
{
    return use_add ? add : &subtract; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-3-2]
}

int main()
{
    BinaryOp op = choose(true);
    return op(7, 4);
}
