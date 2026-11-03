int main()
{
    bool lhs = true;
    bool rhs = false;
    int data[2] = {3, 7};
    int value = data[lhs && !rhs];
    return value;
}
