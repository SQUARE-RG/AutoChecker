#include <iostream>

const char* message() {
    return "hello";
}

int main() {
    const char* s = message();
    std::cout << s << std::endl;
    return 0;
}
