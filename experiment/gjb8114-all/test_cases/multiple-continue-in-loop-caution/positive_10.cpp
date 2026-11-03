#include <iostream>
#include <stdexcept>

int main() {
    int i = 0;
    int total = 0;
    while (i < 10) {
        ++i;
        try {
            if (i == 5) {
                continue;
            }
            if (i == 7) {
                throw std::runtime_error("skip");
            }
            total += i;
        } catch (const std::runtime_error& e) {
            std::cerr << "caught: " << e.what() << '\n';
            break;
        }
    }
    std::cout << total << '\n';
    return 0;
}
