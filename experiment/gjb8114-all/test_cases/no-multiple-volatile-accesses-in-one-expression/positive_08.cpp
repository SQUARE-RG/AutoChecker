int main()
{
    volatile int v = 1;
    int snapshot = v;
    int result = (static_cast<void>(snapshot), snapshot + 1);
    return result;
}
