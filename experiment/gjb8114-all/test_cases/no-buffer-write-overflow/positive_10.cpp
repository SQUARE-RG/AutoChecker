#include <algorithm>

int main() {
    int src[4] = {1, 2, 3, 4};
    int dst[2] = {0, 0};
    std::transform(src, src + 2, dst, [](int v) { return v; });
    return 0;
}
