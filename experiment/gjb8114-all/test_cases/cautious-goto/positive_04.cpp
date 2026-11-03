#include <cstdio>

int main() {
    int total = 0;
    for (int i = 0; i < 10; ++i) {
        if (i % 3 == 0) {
            continue;
        }
        total += i;
    }
    std::printf("%d\n", total);
    return 0;
}
