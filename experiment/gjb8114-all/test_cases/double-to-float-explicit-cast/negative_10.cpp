struct Holder
{
    float value;
    explicit Holder(double d) : value(d) {} // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-10-3]
};

int main()
{
    Holder h(3.14);
    return 0;
}
