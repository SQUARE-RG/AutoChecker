#include <iostream>

void process(int mode) {
    int bonus = 10;
    switch (mode) {
        case 1:
            std::cout << "processing mode 1\n";
            break;
        default:
            std::cout << "default\n";
            break;
    }
    std::cout << bonus << '\n';
}

int main() {
    process(1);
    return 0;
}
