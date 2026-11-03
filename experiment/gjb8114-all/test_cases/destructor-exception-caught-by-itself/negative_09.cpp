#include <string>

class Foo {
public:
    ~Foo() noexcept(false);
};

Foo::~Foo() noexcept(false) {
    throw std::string("cleanup failed"); // CHECK-MESSAGES: :[[@LINE]]:5: warning: {{.*}} [ucassaat-r-2-3-2]
}

int main() {
    try {
        Foo f;
    } catch (const std::string&) {
    }
    return 0;
}
