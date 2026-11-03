int add_one(int value) { return value + 1; }

template <int (*Operation)(int)> // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-3-1]
int apply(int value) {
    return Operation(value);
}

int main() {
    return apply<&add_one>(41);
}
