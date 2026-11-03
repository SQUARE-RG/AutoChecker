class Calculator
{
public:
    int value(void) noexcept;
};

int Calculator::value(void) noexcept
{
    return 42;
}

int main(void)
{
    Calculator c;
    return c.value();
}
