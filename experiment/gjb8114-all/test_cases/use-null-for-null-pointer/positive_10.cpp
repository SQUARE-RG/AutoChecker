#include <cstddef>

struct Holder {
    int* ptr;
    int value;
};

int main() {
    int value = 7;
    Holder holder = { NULL, value };
    return holder.ptr == NULL ? 0 : 1;
}
