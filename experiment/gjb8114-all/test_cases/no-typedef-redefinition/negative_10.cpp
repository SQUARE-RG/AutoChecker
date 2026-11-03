int main()
{
    typedef int local_value;
    local_value outer = 0;
    auto f = []()
    {
        typedef float local_value; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-3]
        local_value v = 1.5;
        return v;
    };
    (void)outer;
    (void)f();
    return 0;
}
