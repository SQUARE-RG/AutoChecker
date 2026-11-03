template <class... Ts> // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-2-9-1]
struct Tuple {
    static constexpr int size = sizeof...(Ts);
};

int main() {
    Tuple<int, double> t;
    (void)t;
    return Tuple<int, double>::size;
}
