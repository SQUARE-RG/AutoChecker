#include <cstdint>

int main() {
    int value = 42;
    unsigned int* unsigned_ptr = reinterpret_cast<unsigned int*>(&value);
    *unsigned_ptr = 7u;
    return value;
}
