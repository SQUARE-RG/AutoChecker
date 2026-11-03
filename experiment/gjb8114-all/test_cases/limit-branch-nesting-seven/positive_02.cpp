#include <iostream>

int mixed_nesting(int a, int b, int c, int d, int e, int& out) {
    switch (a) {
    case 1:
        switch (b) {
        case 1:
            switch (c) {
            case 1:
                switch (d) {
                case 1:
                    if (e > 0) {
                        if (e > 1) {
                            if (e > 2) {
                                out = 1;
                            }
                        }
                    }
                    break;
                default:
                    out = 0;
                    break;
                }
                break;
            default:
                out = 0;
                break;
            }
            break;
        default:
            out = 0;
            break;
        }
        break;
    default:
        out = 0;
        break;
    }
    return out;
}

int main() {
    int value = 0;
    std::cout << mixed_nesting(1, 1, 1, 1, 3, value) << '\n';
    return 0;
}
