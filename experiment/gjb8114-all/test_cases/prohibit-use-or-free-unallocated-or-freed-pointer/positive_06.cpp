#include <cstdlib>

int main() {
    int* block = static_cast<int*>(std::malloc(4 * sizeof(int)));
    if (block != nullptr) {
        {
            int* middle = block + 1;
            *middle = 21;
            block[2] = 22;
        }
        std::free(block);
        block = nullptr;
    }
    return 0;
}
