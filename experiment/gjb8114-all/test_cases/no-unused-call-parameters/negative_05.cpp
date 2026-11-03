template <typename T>
T first(T value, T unused) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-7-2]
    return value;
}

int main() {
    return first(1, 2);
}
