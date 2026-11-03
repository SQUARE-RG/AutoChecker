#include <iostream>
#include <string>

int main() {
    try {
        throw std::string("value error");
    } catch (const std::string& message) {
        std::cout << message << '\n';
    }
    return 0;
}
