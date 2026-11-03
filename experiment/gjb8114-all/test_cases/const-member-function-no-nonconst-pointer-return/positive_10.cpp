#include <array>

class Store {
public:
    const int* data() const {
        return values_.data();
    }

private:
    std::array<int, 4> values_ = {1, 2, 3, 4};
};

int main() {
    const Store store;
    const int* p = store.data();
    return p[0];
}
