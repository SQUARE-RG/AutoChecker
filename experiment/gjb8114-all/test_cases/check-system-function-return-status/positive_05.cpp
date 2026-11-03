#include <cstdlib>
#include <iostream>

int main() {
    const char* cmd = "echo hello";
    if (const int status = std::system(cmd); status != 0) {
        std::cerr << "command failed: " << status << '\n';
        return 1;
    }
    return 0;
}
