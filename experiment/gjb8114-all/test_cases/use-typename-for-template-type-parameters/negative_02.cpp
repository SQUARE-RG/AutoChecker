template <class T>  // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-2-9-1]
T identity(T value) {
    return value;
}

int main() {
    return identity(7);
}
