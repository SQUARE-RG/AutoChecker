#include <iostream>
#include <string_view>

int main() {
    std::string_view view = "hello";
    if ("hello" == view) {
        std::cout << 1 << std::endl;
    }
    return 0;
}
