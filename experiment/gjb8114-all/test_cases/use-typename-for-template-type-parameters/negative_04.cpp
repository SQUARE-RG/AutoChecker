template <class T> constexpr T default_value = T{};  // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-2-9-1]

int main() {
    return static_cast<int>(default_value<int>);
}
