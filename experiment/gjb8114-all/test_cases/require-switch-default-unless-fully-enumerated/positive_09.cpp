#include <iostream>

int getMode() { return 1; }

int main() {
    int result = 0;
    switch (getMode()) {
        case 0:
            return 0;
        case 1:
            return 1;
        case 2:
            return 2;
        default:
            return -1;
    }
    return result;
}
