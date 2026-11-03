using FixedCallback = int (*)(int, int);

int add(int lhs, int rhs)
{
    return lhs + rhs;
}

int main()
{
    FixedCallback callback = add;
    return callback(1, 2);
}
