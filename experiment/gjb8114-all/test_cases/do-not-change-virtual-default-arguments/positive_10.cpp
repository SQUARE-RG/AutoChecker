#include <string>

class Base {
public:
    virtual ~Base() = default;
    virtual std::string describe(std::string prefix = std::string("same")) const {
        return prefix;
    }
};

class Derived : public Base {
public:
    std::string describe(std::string caption = std::string{"same"}) const override;
};

std::string Derived::describe(std::string caption) const {
    return caption;
}

int main() {
    Derived d;
    std::string result = d.describe();
    (void)result;
    return 0;
}
