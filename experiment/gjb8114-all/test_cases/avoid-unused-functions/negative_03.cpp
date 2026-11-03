template <typename T>
T unused_transform(T value) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-8-3]
    return value;
}

int main() {
    return 0;
}
