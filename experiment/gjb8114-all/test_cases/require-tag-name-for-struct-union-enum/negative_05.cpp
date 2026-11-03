struct S_Container
{
    union // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-8]
    {
        int integer;
        float real;
    };
};

int main()
{
    S_Container s;
    s.integer = 7;
    return s.integer;
}
