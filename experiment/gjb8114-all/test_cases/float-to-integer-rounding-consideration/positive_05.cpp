#include <cmath>

int main() {
    double pages = 17.2;
    int pageCount = static_cast<int>(std::ceil(pages));
    return pageCount == 18 ? 0 : 1;
}
