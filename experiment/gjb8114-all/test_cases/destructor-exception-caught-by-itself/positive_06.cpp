#include <iostream>
#include <new>

class Cleaner {
public:
    int state;
    Cleaner();
    ~Cleaner();
};

Cleaner::Cleaner() : state(1) {}

Cleaner::~Cleaner() {
    try {
        throw std::bad_alloc{};
    } catch (const std::bad_alloc& e) {
        std::cout << e.what() << std::endl;
    }
}

int main() {
    Cleaner c;
    return 0;
}
