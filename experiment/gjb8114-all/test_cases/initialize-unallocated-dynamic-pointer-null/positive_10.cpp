#include <cstdlib>

int main() {
    int** pp = nullptr;
    pp = static_cast<int**>(std::malloc(sizeof(int*)));
    if (pp != nullptr) {
        *pp = nullptr;
    } else {
        return -1;
    }
    std::free(pp);
    return 0;
}
