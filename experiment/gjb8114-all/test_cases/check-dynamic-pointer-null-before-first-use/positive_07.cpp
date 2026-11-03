#include <cstdlib>
#include <cstring>

int main() {
    double* value = static_cast<double*>(std::malloc(sizeof(double)));
    if (value == nullptr) {
        return -1;
    }
    std::memset(value, 0, sizeof(double));
    return 0;
}
