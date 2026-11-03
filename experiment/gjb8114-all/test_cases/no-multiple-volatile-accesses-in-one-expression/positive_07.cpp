int main()
{
    volatile int v = 1;
    int snapshot = v;
    int result = (snapshot > 0) ? snapshot + 1 : 0;
    return result;
}
