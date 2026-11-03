class Calculator
{
public:
    int value(); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-23]
};

int Calculator::value(void)
{
    return 42;
}

int main(void)
{
    Calculator c;
    return c.value();
}
