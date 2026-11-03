#include <iostream>
#include <string>

int main() {
    try {
        throw std::string("hello");
    }
    catch (std::string& s) {
        std::cout << s << std::endl;
    }
    catch (...) {
        std::cout << "unknown" << std::endl;
    }
    return 0;
}
