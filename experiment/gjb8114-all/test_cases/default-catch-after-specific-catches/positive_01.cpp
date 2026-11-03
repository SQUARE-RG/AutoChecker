#include <iostream>

int main() {
    try {
        throw 42;
    } catch (int e) {
        std::cout << "int catch: " << e << "\n";
    } catch (...) {
        std::cout << "default catch\n";
    }
    return 0;
}
