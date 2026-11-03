#include <cstdlib>

int main() {
    switch (std::system("echo hello")) {
        case 0:
            return 0;
        default:
            return 1;
    }
}
