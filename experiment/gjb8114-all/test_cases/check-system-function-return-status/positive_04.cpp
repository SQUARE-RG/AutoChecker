#include <cstdlib>
#include <iostream>

int main() {
    const bool command_ok = (std::system("exit 0") == 0);
    if (!command_ok) {
        std::cout << "command failed\n";
        return 1;
    }
    std::cout << "command succeeded\n";
    return 0;
}
