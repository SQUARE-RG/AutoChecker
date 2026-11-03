#include <cstdlib>

int main() {
    int* arr[2] = {nullptr, nullptr};
    arr[0] = static_cast<int*>(std::malloc(sizeof(int)));
    if (arr[0] != nullptr) {
        *arr[0] = 1;
        std::free(arr[0]);
    }
    return 0;
}
