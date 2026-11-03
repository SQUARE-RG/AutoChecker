struct Widget {
    typedef int value_type;

    void compute()
    {
        typedef float value_type; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-3]
        value_type x = 1.5f;
        (void)x;
    }
};

int main()
{
    Widget w;
    w.compute();
    return 0;
}
