template <typename... Ts>
struct Tuple {
    static constexpr int size = sizeof...(Ts);
};

int main() {
    Tuple<int, double> t;
    (void)t;
    return Tuple<int, double>::size;
}
