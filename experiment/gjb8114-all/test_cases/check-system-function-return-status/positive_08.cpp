#include <cstdlib>

int main() {
    while (std::system("echo hello") != 0) {
        return 1;
    }
    return 0;
}
