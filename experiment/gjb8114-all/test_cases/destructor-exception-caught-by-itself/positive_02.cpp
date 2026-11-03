#include <iostream>
#include <stdexcept>

class Bar {
public:
    int value;
    Bar() : value(0) {}
    ~Bar() {
        try {
            if (value >= 0) {
                throw std::runtime_error("destructor failure");
            }
        } catch (const std::exception& e) {
            std::cout << e.what() << '\n';
        } catch (...) {
        }
    }
};

int main() {
    Bar b;
    return 0;
}
