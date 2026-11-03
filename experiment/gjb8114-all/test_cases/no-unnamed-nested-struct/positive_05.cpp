struct Base
{
    int kind;
};

struct Outer
{
    int id;
    struct Inner : Base { int value; } inner;
};

int main()
{
    Outer outer;
    outer.id = 1;
    outer.inner.value = 2;
    outer.inner.kind = 3;
    return 0;
}
