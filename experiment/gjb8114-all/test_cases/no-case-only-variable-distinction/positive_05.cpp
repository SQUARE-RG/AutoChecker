#include <tuple>

int main() {
    int data = 0;
    auto [DataSet, other] = std::make_tuple(1, 2);
    return data + DataSet + other;
}
