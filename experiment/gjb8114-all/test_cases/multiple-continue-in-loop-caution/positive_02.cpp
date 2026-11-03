#include <iostream>

int main() {
    int values[] = {3, 0, 4};
    int i = 0;
    int sum = 0;
    do {
        int v = values[i++];
        if (v == 0) {
            continue;
        }
        sum += v;
    } while (i < 3);
    std::cout << sum << '\n';
    return 0;
}
