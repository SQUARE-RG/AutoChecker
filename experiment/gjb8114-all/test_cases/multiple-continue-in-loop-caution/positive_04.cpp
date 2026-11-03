#include <iostream>

int main() {
    int result = 0;
    for (int i = 0; i < 10; ++i) {
        switch (i % 3) {
        case 0:
            result += i;
            break;
        case 1:
            if (i > 4) {
                continue;
            }
            result -= i;
            break;
        default:
            result += 2 * i;
            break;
        }
    }
    std::cout << result << std::endl;
    return 0;
}
