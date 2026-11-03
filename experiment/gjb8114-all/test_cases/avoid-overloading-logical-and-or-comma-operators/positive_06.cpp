#include <iostream>

struct Range {
    int lo;
    int hi;

    bool contains(int value) const {
        return value >= lo && value <= hi;
    }
};

int main() {
    Range r{1, 5};
    bool inside = r.contains(3);
    bool valid = inside && (r.lo < r.hi || r.lo == r.hi);
    std::cout << valid << '\n';
    return 0;
}
