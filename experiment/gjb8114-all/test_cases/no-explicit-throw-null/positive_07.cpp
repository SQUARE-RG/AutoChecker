#include <stdexcept>

int validate(int value) {
    if (value < 0) {
        throw std::invalid_argument("negative value");
    }
    return value;
}

int main() {
    return validate(1);
}
