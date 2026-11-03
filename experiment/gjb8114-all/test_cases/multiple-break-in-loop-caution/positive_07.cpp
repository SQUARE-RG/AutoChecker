#include <iostream>

int classify_sum(int x) {
    int sum = 0;
    while (x != 0) {
        switch (x % 3) {
        case 0:
            sum += 1;
            break;
        case 1:
            sum += 2;
            break;
        default:
            sum += 3;
            break;
        }
        if (sum > 10) {
            break;
        }
        --x;
    }
    return sum;
}

int main() {
    std::cout << classify_sum(11) << '\n';
    return 0;
}
