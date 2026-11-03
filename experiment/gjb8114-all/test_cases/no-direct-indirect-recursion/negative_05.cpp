template <typename T>
T triangle_sum(T n) {
    if (n <= T{0}) {
        return T{0};
    }
    return n + triangle_sum(n - T{1}); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-7-16]
}

int main() {
    return static_cast<int>(triangle_sum(4));
}
