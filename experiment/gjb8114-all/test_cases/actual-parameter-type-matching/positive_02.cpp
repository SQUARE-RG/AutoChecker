#include <iostream>

struct Base
{
    virtual ~Base() = default;

    virtual void show() const
    {
        std::cout << "Base" << std::endl;
    }
};

struct Derived : Base
{
    void show() const override
    {
        std::cout << "Derived" << std::endl;
    }
};

void print(const Base& value)
{
    value.show();
}

int main()
{
    Derived derived;
    print(derived);
    return 0;
}
