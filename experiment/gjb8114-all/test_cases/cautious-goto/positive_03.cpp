#include <cstdio>
#include <vector>

int compute(int n) {
    std::vector<int> data(8, 0);
    if (n <= 0) {
        return 0;
    }
    int sum = 0;
    for (int i = 0; i < n && i < 8; ++i) {
        data[i] = i * i;
        sum += data[i];
    }
    return sum;
}

int main() {
    std::printf("%d\n", compute(4));
    return 0;
}
