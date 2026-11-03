#include <iostream>

int nested_ifs(int a, int b, int c, int d, int e, int f, int g) {
    int result = 0;
    if (a > 0) {
        if (b > 0) {
            if (c > 0) {
                if (d > 0) {
                    if (e > 0) {
                        if (f > 0) {
                            if (g > 0) {
                                result = 1;
                            }
                        }
                    }
                }
            }
        }
    }
    return result;
}

int main() {
    std::cout << nested_ifs(1, 1, 1, 1, 1, 1, 1) << '\n';
    return 0;
}
