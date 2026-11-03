#include <iostream>

class AbstractBase {
public:
    AbstractBase() : kind(0) {}
    virtual ~AbstractBase() = default;
    virtual void f() = 0;
private:
    AbstractBase& operator=(AbstractBase const&) = default;
    int kind;
};

int main() {
    return 0;
}
