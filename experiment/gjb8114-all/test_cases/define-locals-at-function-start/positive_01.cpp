#include <cstdio>

double average(int a, int b, int c) {
    double sum = static_cast<double>(a) + b + c;
    double result = sum / 3.0;
    return result;
}

int main() {
    double value = average(1, 2, 4);
    std::printf("%.2f\n", value);
    return 0;
}
