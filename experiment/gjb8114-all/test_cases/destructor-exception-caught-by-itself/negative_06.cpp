#include <iostream>
#include <new>

class Cleaner {
public:
    int state;
    Cleaner();
    ~Cleaner() noexcept(false);
};

Cleaner::Cleaner() : state(1) {}

Cleaner::~Cleaner() noexcept(false) {
    throw std::bad_alloc{}; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-3-2]
}

int main() {
    try {
        Cleaner c;
    } catch (...) {
    }
    return 0;
}
