#include <string>

class Foo {
public:
    ~Foo() noexcept(false);
};

Foo::~Foo() noexcept(false) {
    try {
        throw std::string("cleanup failed");
    } catch (const std::string&) {
    }
}

int main() {
    Foo f;
    return 0;
}
