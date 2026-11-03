struct Base
{
    int kind;
};

struct Outer
{
    int id;
    struct Inner : Base { int value; };  // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-9]
};

int main()
{
    Outer outer;
    outer.id = 1;
    Outer::Inner inner;
    inner.value = 2;
    return 0;
}
