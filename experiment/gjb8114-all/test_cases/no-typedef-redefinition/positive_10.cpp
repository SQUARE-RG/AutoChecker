int main()
{
    typedef int outer_value;
    outer_value outer = 0;
    auto f = []()
    {
        typedef float inner_value;
        inner_value v = 1.5;
        return v;
    };
    (void)outer;
    (void)f();
    return 0;
}
