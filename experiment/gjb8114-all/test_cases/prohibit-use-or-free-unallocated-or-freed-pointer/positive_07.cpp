#include <cstdlib>

int main() {
    int *values = static_cast<int *>(std::calloc(3, sizeof(int)));
    if (values == nullptr) {
        return 0;
    }
    for (int i = 0; i < 3; ++i) {
        values[i] = i + 1;
    }
    int sum = values[0] + values[1] + values[2];
    std::free(values);
    values = nullptr;
    return sum;
}
