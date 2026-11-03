#include <cstdlib>
#include <iostream>

int main() {
    int status = std::system("exit 0");
    switch (status) {
        case 0:
            std::cout << "command succeeded\n";
            break;
        default:
            std::cout << "command failed\n";
            break;
    }
    return 0;
}
