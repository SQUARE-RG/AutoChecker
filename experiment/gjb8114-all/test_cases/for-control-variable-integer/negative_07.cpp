#include <cstdint>

struct Counter {
    std::int32_t value;
    Counter(std::int32_t v = 0) : value(v) {}
    bool operator<(const Counter& rhs) const { return value < rhs.value; }
    Counter& operator++() { ++value; return *this; }
};

int main() {
    Counter total;
    for (Counter c = 0; c < 15; ++c) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-9-2]
    {
        total.value += c.value;
    }
    return total.value > 0 ? 0 : 0;
}
