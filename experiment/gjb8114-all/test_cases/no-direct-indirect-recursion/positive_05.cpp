template <typename T>
T triangle_sum(T n) {
    T total{};
    for (T i = T{1}; i <= n; ++i) {
        total += i;
    }
    return total;
}

int main() {
    return static_cast<int>(triangle_sum(4));
}
