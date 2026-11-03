struct Outer
{
    struct Inner
    {
        int value;
    } inner;

    int data;
};

int main()
{
    Outer o{};
    o.inner.value = 1;
    o.data = 2;
    return o.inner.value + o.data;
}
